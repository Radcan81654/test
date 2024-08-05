#pragma once
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>
#include <string>
#include <vector>
#include <fstream>
#include <experimental/filesystem>
#include "httplib.h"
#include <iostream>
#include <json/json.h>
#include <time.h>
namespace tinker
{
    namespace fs = std::experimental::filesystem;
    class filet
    {
    private:
        std::string file_name;//带路径的文件名
    public:
        filet(const std::string& name)
            :file_name(name){}
        bool file_exists()
        {
            return fs::exists(file_name);
        }
        std::string name()
        {
            size_t pos=file_name.find_last_of("/");
            if(pos==std::string::npos)
            {
                return file_name;
            }
            return file_name.substr(pos+1);
        }
        int64_t file_size()//显示这个函数和getposlen函数错误
        {
            struct stat status;
            //std::cout<<file_name.c_str()<<std::endl;
            if(stat(file_name.c_str(),&status)==-1)
            {
                std::cout<<"file_size->stat false"<<std::endl;
                return -1;
            }
            return status.st_size;
        }
        time_t last_modify_time()
        {
            struct stat status;
            if(stat(file_name.c_str(),&status)==-1)
            {
                std::cout<<"last_modify_time->stat false"<<std::endl;
                return -1;
            }
            return status.st_mtime;

        }
        time_t last_acess_time()
        {
            struct stat status;
            if(stat(file_name.c_str(),&status)==-1)
            {
                std::cout<<"last_acess_time->stat false"<<std::endl;
                return -1;
            }
            return status.st_atime;

        }
        
        bool set_content(const std::string &body)//filet结构体和函数中创建的string类中间对象然只存储文件的名称，
        {/////////////////////////////////////////但是承担了创建文件和与"文件内容"相关操作的一切工作
            std::ofstream ofs;
            ofs.open(file_name,std::ios::binary);
            if(ofs.is_open()==false)
            {
                std::cout<<"set_content->open false"<<std::endl;
                ofs.close();
                return false;
            }
            ofs.write(&body[0],body.size());
            if(ofs.good()==false)
            {
                std::cout<<"set_content->write false"<<std::endl;
                ofs.close();
                return false;
            }
            ofs.close();
            return true;
        }
        bool get_pos_len(std::string &body,int64_t pos,int64_t len)//获取文件从文件"指定位置后指定长度的数据"
        {
            std::ifstream ifs;
            ifs.open(file_name,std::ios::binary);
            if(ifs.is_open()==false)
            {
                std::cout<<"get_pos_len->open false"<<std::endl;
                ifs.close();
                return false;
            }
            int64_t sz=this->file_size();
            if(pos+len>sz)
            {
                std::cout<<"get_pos_len->pos+len false"<<std::endl;
                ifs.close();
                return false;
            }
            ifs.seekg(pos,std::ios::beg);
            body.resize(len);
            ifs.read(&body[0],len);
            if(ifs.good()==false)
            {
                std::cout<<"get_pos_len->read false"<<std::endl;
                ifs.close();
                return false;
            }
            ifs.close();
            return true;

        }
        bool get_content(std::string &body)//注意读取到的数据是“未经反序列化”的
        {
            int64_t sz=this->file_size();
            return get_pos_len(body,0,sz);
        }
        

        bool create_dir()//创建目录
        {
            if(this->file_exists())
                return true;
            return fs::create_directories(file_name);
        }
        bool get_dir(std::vector<std::string> &arr)//遍历文件夹中所有文件的信息
        {
            for(auto& it:fs::directory_iterator(file_name))
            {
                if(fs::is_directory(it))
                    continue;
                arr.push_back(fs::path(it).relative_path().string());
                
            }
            return true;
        }
        bool dl_self()
        {
            if(this->file_exists())
            {
                remove(file_name.c_str());
                return true;
            }
            return false;
        }

        


    };
    class jsont
    {
    public:
        static bool serialize(const Json::Value & root,std::string &str)//传入root后将其序列化为string类型字符串
        {
            Json::StreamWriterBuilder swb;
            std::unique_ptr<Json::StreamWriter> sw(swb.newStreamWriter());
            std::stringstream ret;
            sw->write(root,&ret);
            str=ret.str();
            return true;

        }
        static bool unserialize(const std::string &str,Json::Value &root)//对应的反序列化
        {
            Json::CharReaderBuilder crb;
            std::unique_ptr<Json::CharReader> cr(crb.newCharReader());
            std::string err;
            bool flag=cr->parse(str.c_str(),str.c_str()+str.size(),&root,&err);
            if(flag==false)
            {
                std::cout<<"unserialize->parse false"<<std::endl;
                return flag;
            }
            return flag;
        }

    };




}