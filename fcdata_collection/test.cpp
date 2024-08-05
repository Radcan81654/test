#include "filetrick.hpp"
#include "net_sv.hpp"
#include "sheets_inf.hpp"
#define CPPHTTPLIB_OPENSSL_SUPPORT 

void print_aa_token(tinker::get_aa_token& m)
{
   cout<<"_code:"<<m._code<<endl;
   cout<<"_msg:"<<m._msg<<endl;
   cout<<"_app_access_token:"<<m._app_access_token<<endl;
   cout<<"_expire:"<<m._expire<<endl;
   cout<<"_tenant access token:"<<m._tenant_access_token<<endl;
   cout<<"_aatoken_valid_time:"<<m._aatoken_valid_time<<endl;
   cout<<"内部函数判断是否有效:"<<m.is_aatoken_valid()<<endl;
   cout<<"现在的时间戳"<<time(NULL)<<endl;
   cout<<"现在的时间戳+有效时间"<<(time(NULL)+m._expire)<<endl;    
}
void print_precode(tinker::get_precode& m)
{
   cout<<"_precode:"<<m._precode<<endl;
   cout<<"_precode_valid_time:"<<m._precode_valid_time<<endl;
}
void print_uarftoken(tinker::get_uarftoken& m)
{
    cout<<"_code:"<<m._code<<endl;
    cout<<"_msg:"<<m._msg<<endl;
    cout<<"user_access_token:"<<m._user_access_token<<endl;
    cout<<"_expires_in:"<<m._expires_in<<endl;
    cout<<"uatoken_valid_time:"<<m.uatoken_valid_time<<endl;
    cout<<"_refresh_token:"<<m._refresh_token<<endl;
    cout<<"_refresh_expires_in:"<<m._refresh_expires_in<<endl;
    cout<<"rftoken_valid_time:"<<m._code<<endl;

    
}

void print_read_sheets_info(tinker::read_sheets_info& m)
{
    cout<<"src_sheet_id:"<<m.src_sheet_id<<endl;
    cout<<"ssheet_index:"<<m.ssheet_index<<endl;
    cout<<"ssheet_row_count:"<<m.ssheet_row_count<<endl;
    cout<<"dst_sheet_id:"<<m.dst_sheet_id<<endl;
    cout<<"dsheet_index:"<<m.dsheet_index<<endl;


}

//////////////////////////////////////////////////////////////以上类的成员打印均测试成功

void test1()
{
    //tinker::get_ua_token m;
    //print_ua_token(m);
    tinker::get_aa_token m;
    m.refresh_aatoken();
    print_aa_token(m);
    tinker::get_precode n;
    print_precode(n);
    //tinker::get_aa_token,tinker::get_precode
    //两个类测试无误，可以正常刷新和申请
}

void test2()
{
    tinker::get_uarftoken m;
    print_uarftoken(m);

}

void test3()
{
    tinker::read_sheets_info sts;
    //print_read_sheets_info(sts);//打印内容无误
}

////////////////////////////////////////////////////////////////////////////////////////////////
void test4()
{
    tinker::fdata_collection m;
    m.load_data();
}


int main()
{
    test4();
    return 0;
}
