config_file="config.json"

db_username=$(grep -Po '(?<="db_username": ")[^"]*' $config_file)
db_password=$(grep -Po '(?<="db_password": ")[^"]*' $config_file)
db_host=$(grep -Po '(?<="db_host": ")[^"]*' $config_file)
db_port=$(grep -Po '(?<="db_port": ")[^"]*' $config_file)
db_schema=$(grep -Po '(?<="db_schema": ")[^"]*' $config_file)
domain_name=$(grep -Po '(?<="domain_name": ")[^"]*' $config_file)

alias mysql_cmd="mysql -h $db_host --port=$db_port -u$db_username -p$db_password $db_schema"

# Get list of top level domains
tld_list_url="http://data.iana.org/TLD/tlds-alpha-by-domain.txt"
tld_list_filename="tlds.txt"
curl -s -o $tld_list_filename $tld_list_url

# Perform lookups and store info in database
request_headers="User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36" # I am not a bot

while read tld; do
    if [[ $tld == \#* ]]
    then
        continue #ignore lines commented with hash
    fi
    tld=$(echo "$tld" | awk '{print tolower($0)}')
    request_url="http://goatman.$tld"
    echo $request_url

    # https://stackoverflow.com/a/37072904/5659556
    res=$(curl -sw "%{http_code}" -H "$request_headers" $request_url)
    http_code="${res:${#res}-3}"
    if [ ${#res} -eq 3 ]; then
        body=""
    else
        body="${res:0:${#res}-3}"
    fi

    mysql_cmd -se "CALL update_or_insert_response('$tld', '$request_url', $http_code, NULL, '$body')"

    echo $http_code
    echo $body

done <$tld_list_filename
