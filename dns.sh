#!/bin/bash
#*************************************************
# Description : DNS 管理工具
# Version     : 2.0
# Author      : XABCLOUD.COM
#*************************************************
#-----------------VAR-----------------------------
BASE=/opt/sys
DATE=$(date "+%Y-%m-%d")
ACTION=$1
SubDomain=$2
Type=$3
Value=$4
recordId=$3
[ $ACTION ]||ACTION=HELP
if [ $SubDomain ];then
	DomainName=`echo $SubDomain|awk -F"." '{print $(NF-1)"."$NF}'`
	RR=`echo $SubDomain|awk -F".$DomainName" '{print $1}'`
	if [ $DomainName == "com.cn"  ]||[ $DomainName == "org.cn" ]||[ $DomainName == "gov.cn" ];then
		DomainName=`echo $SubDomain|awk -F"." '{print $(NF-2)"."}'`"$DomainName"
		RR=`echo $SubDomain|awk -F".$DomainName" '{print $1}'`
	fi
	if [ $DomainName == $RR ];then RR="@";fi
fi
SecretId=""
SecretKey=""
access_key_id=""
access_key_secret=""
#-----------------FUN-----------------------------
DomainList(){
	# Qcloud DNS API [获取域名列表]
	# ./dns.sh DomainList
	$BASE/qcloud-dns.py DomainList -u $SecretId -p $SecretKey > $BASE/.Qcloud-domains
	$BASE/listdns.py $BASE/.Qcloud-domains
}
RecordCreate(){
	# Qcloud DNS API [添加解析记录]
	# ./dns.sh RecordCreate [a.example.cm 子域名] [CNAME 记录类型] [base.example.com 记录地址]
	$BASE/qcloud-dns.py RecordCreate -u $SecretId -p $SecretKey --domain $DomainName --subDomain $RR --recordType $Type --value $Value
}
RecordList(){
	# Qcloud DNS API [获取解析记录列表]
	# ./dns.sh RecordList [example.com 主域名]
	$BASE/qcloud-dns.py RecordList -u $SecretId -p $SecretKey --domain $DomainName > $BASE/.$DomainName-RecordList-$DATE
	$BASE/listdns.py $BASE/.$DomainName-RecordList-$DATE > $BASE/.$DomainName-RecordList.list
	cat $BASE/.$DomainName-RecordList.list
}
RecordDelete(){
	# Qcloud DNS API [删除解析记录]
	# ./dns.sh RecordDelete [$domain 主域名] [$recordId 记录ID]
	[ $recordId ]||$BASE/qcloud-dns.py RecordList -u $SecretId -p $SecretKey --domain $DomainName > $BASE/.$DomainName-RecordList-$DATE
	[ $recordId ]||$BASE/listdns.py $BASE/.$DomainName-RecordList-$DATE > $BASE/.$DomainName-List-$DATE
	[ $recordId ]||cat $BASE/.$DomainName-List-$DATE
	[ $recordId ]&&$BASE/qcloud-dns.py RecordDelete -u $SecretId -p $SecretKey --domain $DomainName --recordId $recordId
}
DescribeDomains(){
	# Aliyun DNS API [获取域名列表]
	# ./dns.sh DescribeDomains
	$BASE/aliyun-dns.py Action=DescribeDomains PageSize=100 Id=$access_key_id Secret=$access_key_secret|sed 's/true/True/g;s/false/False/g' > $BASE/.Aliyun-domains
	$BASE/listdns.py $BASE/.Aliyun-domains
}
AddDomainRecord(){
	# Aliyun DNS API [添加解析记录]
	# ./dns.sh AddDomainRecord [a.example.com 子域名] [CNAME 记录类型] [base.example.com 记录地址]
	$BASE/aliyun-dns.py Action=AddDomainRecord DomainName=$DomainName RR=$RR Type=$Type Value=$Value Id=$access_key_id Secret=$access_key_secret
}
DescribeDomainRecords(){
	# Aliyun DNS API [获取解析记录列表]
	# ./dns.sh DescribeDomainRecords [example.com 主域名]
	$BASE/aliyun-dns.py Action=DescribeDomainRecords DomainName=$DomainName PageSize=500 Id=$access_key_id Secret=$access_key_secret|sed 's/true/True/g;s/false/False/g' > $BASE/.$DomainName-RecordList-$DATE
	$BASE/listdns.py $BASE/.$DomainName-RecordList-$DATE > $BASE/.$DomainName-RecordList.list
	cat $BASE/.$DomainName-RecordList.list
}
DeleteSubDomainRecords(){
	# Aliyun DNS API [删除解析记录]
	# ./dns.sh DeleteSubDomainRecords [a.example.cm 子域名] [CNAME 记录类型]
	[ $Type ]||$BASE/aliyun-dns.py Action=DescribeDomainRecords DomainName=$DomainName PageSize=500 Id=$access_key_id Secret=$access_key_secret|sed 's/true/True/g;s/false/False/g' > $BASE/.$DomainName-RecordList-$DATE
	[ $Type ]||$BASE/listdns.py $BASE/.$DomainName-RecordList-$DATE > $BASE/.$DomainName-List-$DATE
	[ $Type ]||cat $BASE/.$DomainName-List-$DATE
	[ $Type ]&&$BASE/aliyun-dns.py Action=DeleteSubDomainRecords DomainName=$DomainName RR=$RR Type=$Type Id=$access_key_id Secret=$access_key_secret
}
HELP(){
	echo "# ./dns.sh DomainList [腾讯云 获取域名列表]"
	echo "# ./dns.sh RecordCreate a.example.cm CNAME base.example.com [腾讯云 添加解析记录]"
	echo "# ./dns.sh RecordList example.com [腾讯云 获取解析记录列表]"
	echo "# ./dns.sh RecordDelete example.com recordId [腾讯云 删除解析记录]"
	echo "# ./dns.sh DescribeDomains [阿里云 获取域名列表]"
	echo "# ./dns.sh AddDomainRecord a.example.com CNAME base.example.com [阿里云 添加解析记录]"
	echo "# ./dns.sh DescribeDomainRecords example.com [阿里云 获取解析记录列表]"
	echo "# ./dns.sh DeleteSubDomainRecords a.example.cm CNAME [阿里云 删除解析记录]"
}
main(){
	case "$ACTION" in
		$ACTION)
			$ACTION
			;;
	esac
}
#-----------------PROG----------------------------
main
