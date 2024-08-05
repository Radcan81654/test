#include "net_sv.hpp"

using namespace std;
//#define DST_SHEET_TOKEN "WmiDsqnzbhEqL3tkj4mcQXHenfb"//把被采集信息输出到里面的目标token
#define SRC_SPREADSHEET_TOKEN "RbqqsliPPhYvRUtQgeCcZ5hxnzg"//需要被采集信息的电子表格的token,自己存的副本
#define SRC_SHEET_TITLE "Sheet1"//必须保证电子表格里面至少有两个工作表(sheet),且均未被隐藏
#define DST_SHEET_TITLE "Sheet2"

#define USER_ID "g68857da"
namespace tinker
{
    //这里少东西，我得先写完怎么组织link们的信息，我才能完成下面这些读取的工作
    class read_sheets_info//先看看报文能不能正常拿到，能拿到的话就开始写前面的部分
    {
        //收集编号，更新日志，文章链接
        //目前已知可以直接通过接口拿到，
        public:
        get_uarftoken uft;//使用之前必须在前面加上"Bearer ",没事的时候用一下refresh_uarftoken()
        string src_sheet_id;
        int ssheet_index;
        int ssheet_row_count;
        //
        string dst_sheet_id;
        int dsheet_index;

 
        //bool is_ssheet_hidden;
        void init_sheets_id()
        {
            httplib::SSLClient cli("open.feishu.cn");
            string m=SRC_SPREADSHEET_TOKEN;
            //我是按"获取手球按登录授权码"和"获取工作表"这两个接口对于"路径参数"的表述完全不同
            string path="/open-apis/sheets/v3/spreadsheets/"+ m +"/sheets/query";
            httplib::Headers headers = {{"Authorization","Bearer "+uft._user_access_token}};
            httplib::Result res=cli.Get(path,headers);
            //httplib::Result res=cli.Get(path,params,headers);
            httplib::Response rsp=res.value();//string类型
            //cout<<"ua_token:"<<uft._user_access_token<<endl;
            //cout<<"rsp.body:"<<rsp.body<<endl;   
            string tmp=rsp.body;
            //cout<<"原始报文内容:"<<tmp<<endl;
            jsont jt;
	        Json::Value jv1;
	        jt.unserialize(tmp,jv1);

            Json::Value sd=jv1["data"]["sheets"];
            for(int i=0;i<2;i++)//这就要求电子表格里面只有源工作表和目标工作表两张工作表
            {
                //cout<<"sd[i]:"<<sd[i]<<endl;//没问题
                if(sd[i]["title"]==SRC_SHEET_TITLE)//源工作表
                {
                    src_sheet_id=sd[i]["sheet_id"].asString();
                    ssheet_index=sd[i]["index"].asInt();
                    ssheet_row_count=sd[i]["grid_properties"]["row_count"].asInt();
                }
                else//目标工作表
                {
                    dst_sheet_id=sd[i]["sheet_id"].asString();
                    dsheet_index=sd[i]["index"].asInt();

                }
                

            }
        }
        void read_ssheet()
        {
            httplib::SSLClient cli("open.feishu.cn");
            string q=SRC_SPREADSHEET_TOKEN;
            string path="/open-apis/sheets/v2/spreadsheets/"+ q +"/values_batch_get";
            httplib::Headers headers = {{"Authorization","Bearer "+uft._user_access_token},{"Content-Type","application/json; charset=utf-8"}};
            httplib::Params params;
            string s_ranges=src_sheet_id+"!"+"B1:"+"B"+to_string(ssheet_row_count);
            params.emplace("ranges",s_ranges);
            httplib::Result res=cli.Get(path,params,headers);
            httplib::Response rsp=res.value();//string类型  

            string tmp=rsp.body;
            jsont jt;
	        Json::Value jv1;
	        jt.unserialize(tmp,jv1);
            //直接从jv1提取
            
            filet k("sheet_tmp_inf.dat");
            k.dl_self();
            string eg;
            k.set_content(tmp);
            cout<<"表格链接等信息已被输出至sheet_tmp_inf.dat"<<endl;
            cout<<"这就是目前为止完成的信息采集"<<endl;


        }
        //然后开始考虑怎么读
        read_sheets_info()
        {
            init_sheets_id();
            read_ssheet();
        }

    };
    ////////////////
    class single_link_info//功能是描述"一个链接对应的信息"
    {
        public://必须全是public成员
        int _number;//这个链接的索引
        string _link;
        string _title;
        //前两个只要读到就能初始化，后两个应该得等chatgpt接入
        string _updatelogs;
        time_t _keyword;
        time_t _summary;
 
    };



//止步于此，读不出干净的文章链接，表格里面链接那列不填链接的emoji不会处理
/////////////////////////////////////////////////////////////////////
    class fdata_collection
    {
        public:
        read_sheets_info rsi;
        unordered_map<int,single_link_info> umap;//文件操作的时候就可以顺便把更新日志写了

        bool insert_data(single_link_info& m)
        {
            umap[m._number]=m;
            umap[m._number]._updatelogs="插入数据";
            return true;
        }
        bool update_data(single_link_info& m)
        {
            umap[m._number]=m;
            umap[m._number]._updatelogs="更新数据";

            return true;
        }
        bool numget_single_data(int& number,single_link_info& m)
        {
            auto it=umap.find(number);
            if(it==umap.end())
            {
                return false;
            }
            m=umap[number];
            return true;

        }
        bool load_data()
        {
            filet m("sheet_tmp_inf.dat");
            if (m.file_exists() == false)
                return true;
            string content;
            m.get_content(content);
            Json::Value jv;
            jsont::unserialize(content, jv);
            Json::Value arr=jv["data"]["valueRanges"][0]["values"];//显示为null
        
            for(int i=1;i<arr.size()&&arr.isArray()&&arr[i].isArray()&&arr[i][0].isArray()&&arr[i][0][0].isArray();i++)//
            {
                cout<<"i:"<<i<<endl;
                single_link_info tmp;
                tmp._number=i;
                tmp._link=arr[i][0][0]["link"].asString();
                tmp._title=arr[i][0][0]["text"].asString();
                

                insert_data(tmp);
            }
            cout<<"载入数据完成,以下为具体数据:"<<endl;
            for(auto it:umap)
            {
                cout<<it.first<<"-"<<it.second._link<<endl;
            }
            
            
           return true;

        }
        bool get_all_data(vector<single_link_info> arr)
        {


            return true;
        }
        bool save_data()
        {
            //把存放在哈希表里面的东西存储到"sheet_inf.dat"里面，
            //相当于是把sheet_tmp_inf_dat里面原始的内容提取了一下
            return true;
        }



    };
    














    class gdata_collection//采集完了以后收集信息
    {
        //找摘要和标签
        


    };


}