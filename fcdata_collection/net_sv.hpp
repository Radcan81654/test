#pragma once
#define CPPHTTPLIB_OPENSSL_SUPPORT 
#include "httplib.h"
#include <openssl/err.h>
#include <sstream>
#include "filetrick.hpp"
#include <sys/wait.h>
#define SOUSE_SHEET_TOKEN "n5wts8v9wh3gxjtyxpvcdbmznjc"
#define APP_ID "cli_a6109595397dd00c"
#define APP_SECRET "4kvnWi7eSELx5lLyQv7NkgsRJMoBL8yc"
#define REDIRECT_URI "https%3A%2F%2F123.56.166.61%2Fmock"
////https://123.56.166.61/mock经过application/x-www-form-urlencoded编码以后的格式
using namespace std;
namespace tinker
{
    class get_aa_token//只负责获得app_access_token
    {
        public:
        int _code;//错误码
        string _msg;//错误码描述
        string _app_access_token;
        int _expire;
        string _tenant_access_token;
        time_t _aatoken_valid_time;//此处的validtime指的都是(生产日期+保质期)   

        void init_aatoken()
        {
            //"https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
            httplib::SSLClient cli("open.feishu.cn");
            httplib::Headers headers = {{"Content-Type","application/json; charset=utf-8"}};
            Json::Value jv;
            //初始化请求体内容：
            jv["app_id"]=APP_ID;
            jv["app_secret"]=APP_SECRET;
            string jret;
            jsont jt;
            jt.serialize(jv,jret);//jret就是组织好的字符串
            //cout<<jret<<endl;//无误
            httplib::Result res=cli.Post("/open-apis/auth/v3/app_access_token/internal",headers,jret,"application/json");
            // cout<<"res.error():"<<res.error()<<endl;          
            httplib::Response rsp=res.value();
	        string tmp=rsp.body;
	        Json::Value jv1;
	        jt.unserialize(tmp,jv1);
            _code=jv1["code"].asInt();
            _msg=jv1["msg"].asString();
            _app_access_token=jv1["app_access_token"].asString();
            _expire=jv1["expire"].asInt();
            _tenant_access_token=jv1["tenant_access_token"].asString();
            _aatoken_valid_time=time(NULL)+_expire;
            return;     
        }  
        bool is_aatoken_valid()
        {
            return ((time(NULL)<_aatoken_valid_time)&&(_code==0));//可能后续会改一下类型
            //没过期且错误码为0
        }
        void refresh_aatoken()
        {
            while(!(is_aatoken_valid()))
            {
                cout<<"app_access_token正在更新"<<endl;

                init_aatoken();
            }
            cout<<"app_access_token初始/更新完毕"<<endl;
            return;
        }
        //
        get_aa_token()
        {
            init_aatoken();

        }
    };
    //----------------------------------------------------------
    class get_precode
    {
        public:
        string _precode;//登陆预授权码
        time_t _precode_valid_time;//过期的时间戳
        void init_precode()
        {
            //eg:
            //GET https://open.feishu.cn/open-apis/authen/v1/authorize?app_id=cli_a219a18a64f8d01b&redirect_uri=https%3A%2F%2F127.0.0.1%2Fmock&scope=bitable:app:readonly%20contact:contact&state=RANDOMSTATE   
            stringstream url;
            string scope = "drive:drive docs:doc sheets:spreadsheet";
            url << "/open-apis/authen/v1/authorize"
                << "?app_id=" << APP_ID
                << "&redirect_uri="<<REDIRECT_URI
                << "&scope=" << scope
                << "&state=RANDOMSTATE";
            
            string path=url.str();
            //cout<<path<<endl;
            httplib::SSLClient cli("open.feishu.cn");
            auto res=cli.Get(path);
            string location = res->get_header_value("Location");
            cout << "重定向到: " << location << endl;
            cout<<"请手动打开上述链接:"<<endl;
            httplib::SSLServer svr("/root/zhengshu/selfsigned.crt","/root/zhengshu/selfsigned.key");
            svr.Get("/mock", [&](const httplib::Request& req, httplib::Response& res) 
            {
                auto code = req.get_param_value("code");
                auto state = req.get_param_value("state");
                if (!code.empty()) 
                {
                    _precode=code;
                    _precode_valid_time=time(NULL)+300;//登陆预授码的有效时间为300s
                    //cout<<"_precode:"<<_precode<<endl;
                    cout << "授权码已完成初始化: "  << endl;
                    res.set_content("If the terminal information does not change, please reauthorize\nAuthorization successful, you can close this window.", "text/plain");
                    svr.stop();
                }
                else
                {
                    res.set_content("Authorization failed??", "text/plain");
                    
                }


            });
            cout << "HTTPS 服务器启动，等待授权重定向..." << endl;
            svr.listen("0.0.0.0", 443);//httplib是一个阻塞式的库
            
        }

        bool is_precode_valid()
        {
            return time(NULL)<_precode_valid_time;
        }
        void refresh_precode()
        {
            if(!is_precode_valid())//不能用while,否则会一直在跳“授权码更新中”
            {
                cout<<"登录预授权码更新中"<<endl;
                init_precode();
                cout<<"登录预授权码更新完毕"<<endl;
                return;


            }
            cout<<"登录授权码更新失败"<<endl;
            return;

            
        }
        get_precode()
        {
            init_precode();
        }

    };

    class get_uarftoken
    {
        public:
        int _code;//错误码，非 0 表示失败
        string _msg;//错误描述
        string _user_access_token;
        int _expires_in;//user_access_token有效期，单位: 秒，有效时间两个小时左右
        time_t uatoken_valid_time;
        string _refresh_token;//刷新user_access_token时使用的 refresh_token，感觉不用这个东西的话，每2个小时（每当user_access_token过期），用户就要重新授权一遍,但如果用这个刷新，用户一个月授权一次就好
        int _refresh_expires_in;
        time_t rftoken_valid_time;
        //token_type和scope和后续没关联，所以没初始化
        void init_uarftoken()
        {
            get_aa_token aat;//string _app_access_token
            get_precode gp;//string _precode

            httplib::SSLClient cli("open.feishu.cn");
            aat.refresh_aatoken();
            httplib::Headers headers = {{"Authorization",aat._app_access_token},{"Content-Type","application/json; charset=utf-8"}};
            Json::Value jv;
            jv["grant_type"]="authorization_code";
            gp.refresh_precode();
            jv["code"]=gp._precode;
            jv["app_access_token"]=aat._app_access_token;
            string jret;
            jsont jt;
            jt.serialize(jv,jret);//jret就是组织好的字符串
            //https://open.feishu.cn/open-apis/authen/v1/oidc/access_token
            httplib::Result res=cli.Post("/open-apis/authen/v1/oidc/access_token",headers,jret,"application/json");
            //提取响应报文
            httplib::Response rsp=res.value();
            string tmp=rsp.body;
            //cout<<"原始报文内容:"<<tmp<<endl;
	        Json::Value jv1;
	        jt.unserialize(tmp,jv1);
            //取出自己想要的部分
	        _code=jv1["code"].asInt();
            _msg=jv1["msg"].asString();

            if(_code==0)
            {
                cout<<"已获得user_access_token"<<endl;
                //这部分以后的data在文档里的描述是token_info,但是看起来像是json
	            Json::Value _data=jv1["data"];//从报错里看出来的这个部分本身就是Json::Value类型的，不需要转换成string
                //cout<<"jv1[""data""]:"<<jv1["data"]<<endl;
                _user_access_token=_data["access_token"].asString();
                _expires_in=_data["expires_in"].asInt();
                uatoken_valid_time=time(NULL)+_expires_in;

                _refresh_token=_data["refresh_token"].asString();
                _refresh_expires_in=_data["refresh_expires_in"].asInt();
                rftoken_valid_time =time(NULL)+_refresh_expires_in;
                
                return;

            }
        }
        bool is_rftoken_valid()
        {
            //rftoken过期了就直接两个一起刷新
            //否则只借助rftoken刷新uatoken就行了
            return time(NULL)<rftoken_valid_time;

        }
        bool is_uatoken_valid()
        {
            return time(NULL)<uatoken_valid_time;
        }

        void refresh_uarftoken()
        {
            //由于我不知道哪部分过期了哪部分没过期，所以封装成一个函数
            //思路是先判断rf_token是否过期，如果rftoken没过期就用rftoken刷新，否则才调用init_uarftoken()两个一起刷新
            while((!is_uatoken_valid())&&(is_rftoken_valid()))
            {
                cout<<"根据refresh_token刷新user_access_token中"<<endl;
                get_aa_token aat;//string _app_access_token
                httplib::SSLClient cli("open.feishu.cn");
                string path="/open-apis/authen/v1/refresh_access_token";
                aat.refresh_aatoken();
                httplib::Headers headers = {{"Authorization",aat._app_access_token},{"Content-Type","application/json; charset=utf-8"}};
                Json::Value jv;
                jv["grant_type"]="refresh_token";        
                jv["refresh_token"]=_refresh_token;            
                string jret;
                jsont jt;
                jt.serialize(jv,jret);//jret就是组织好的字符串

                httplib::Result res=cli.Post(path,headers,jret,"application/json");
                //提取响应报文
                httplib::Response rsp=res.value();
                string tmp=rsp.body;
            
	            Json::Value jv1;
	            jt.unserialize(tmp,jv1);
                //从jv1里面取出自己想要的部分
                if(jv1["code"]==0)
                {
                    Json::Value j;
                    _user_access_token=j["user_access_token"].asString();
                    _expires_in=j["expires_in"].asInt();
                    uatoken_valid_time=time(NULL)+_expires_in;

                }
                else
                {
                    cout<<"根据refresh_token重新获取user_access_token失败"<<endl;
                }

            }
            while((!is_uatoken_valid())&&(!is_rftoken_valid()))
            {
                cout<<"请重新授权"<<endl;
                init_uarftoken();
                return;
            }
            cout<<"刷新user_access_token成功"<<endl;
            return;


        }
        get_uarftoken()
        {
            //构造函数
            init_uarftoken();
        }


    };
    //感觉内容已经太多了，所以这个头文件就先这些内容
    
    
    














}
