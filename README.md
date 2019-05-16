>在业务域名日常管理操作中,我们需要反复登录阿里云或者腾讯云的云控制台,比如新的业务上线,在 Nginx 加段 server {} 后,直接使用下面工具可以更加快捷的对域名管理,不需要反复登录云服务商管理控制台

![](//s.xabcloud.com/_media/dns.png)

## 原理

使用云服务商提供的域名管理 API 实现对域名解析管理的操作,主要是下列几项:

- 添加解析记录
- 删除解析记录
- 获取解析记录列表

因为阿里云和腾讯云各自的 API 接口实现并不相同,所以这里提供的 `dns.sh` 对二者略微简单的封装,使得操作更简易明了

## 资源

相关工具脚本资源我们收集在这里 [dns.tgz](https://s.xabcloud.com/file/dns.tgz)

<b>_需要说明的是,这些日常工具在我们的一体化运维管控平台各个 Master 机器的 /opt/sys/ 路径下默认有生成,所以里面脚本的路径也是/opt/sys/,可以根据需要自己修改即可_</b>

## 工具文件简单说明

- dns.sh 是执行脚本
- qcloud-api.py 是腾讯云域名API工具
- aliyun-api.py 是阿里云域名API工具
- listdns.py 是域名解析记录列表工具(默认获取的解析记录是一个 JSON 数据结构,这个列表工具可以明了的一行行展现域名解析记录,比如腾讯云删除解析记录,需要传参子域名ID,所以这里首先可以获取记录列表,确认待删除子域名的ID,然后删除;而阿里云那边需要传参域名记录类型,然后就全部删除,比如一个子域名有多个A记录,那么就一次性删除了该子域名所有A记录)

# dns.sh 文件说明

如果域名管理在阿里云上,那么补全变量 `access_key_id 和 access_key_secret`  
如果域名管理在腾讯云上,则需要补全变量 `SecretId 和 SecretKey`

```bash
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
```

# 添加域名解析

```bash
# ./dns.sh RecordCreate test.xabcstack.com CNAME xabcdns.com  (腾讯云添加 test.xabcstack.com CNAME xabcdns.com)
# ./dns.sh RecordCreate test1.xabcstack.com A 112.111.111.11 (腾讯云添加 test1.xabcstack.com A记录 112.111.111.11)
# ./dns.sh AddDomainRecord test.xabc.tech CNAME xabcloud.com (阿里云添加 test.xabc.tech CNAME xabcdns.com)
# ./dns.sh AddDomainRecord test1.xabc.tech A 112.111.111.11 (阿里云添加 test1.xabc.tech A记录 112.111.111.11)
```

# 获取域名解析记录列表

```bash
# ./dns.sh RecordList xabcloud.com (腾讯云获取 xabcloud.com 域名解析记录列表）
# ./dns.sh DescribeDomainRecords xabc.tech (阿里云获取 xabc.tech 域名解析记录列表)
```

# 删除域名解析

对腾讯云来说,删除域名解析记录,关键是确认域名记录ID,然后删除;所以我们就先获取域名解析列表信息,其中第一个字段就是域名记录ID,然后我们再删除  
对阿里云来说,删除域名解析记录,只要确认子域名和解析类型即可删除  
如下图示例,其中 xabcstack.com 域名管理在腾讯云,而 xabc.tech 域名管理在阿里云

![](//s.xabcloud.com/_media/qddns.png)
![](//s.xabcloud.com/_media/addns.png)

?> 参考 [腾讯云 API](https://cloud.tencent.com/document/api) [阿里云 API](https://developer.aliyun.com/api)
