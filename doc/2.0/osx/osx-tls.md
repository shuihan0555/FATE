# 证书生成：

two-way TSL：

## 1）方式一：使用keystore密码箱存储私钥、证书、信任证书方式

####  生成client和server端的秘钥keystore文件、证书文件、信任证书链，具体命令步骤如下：

 1. 创建一个包含服务器公钥和私钥的密钥库，并为其指定了一些属性：

    ```
    keytool -v -genkeypair -dname "CN=OSX,OU=Fate,O=WB,C=CN" -keystore server/identity.jks -storepass 123456 -keypass 123456 -keyalg RSA -keysize 2048 -alias server -validity 3650 -deststoretype pkcs12 -ext KeyUsage=digitalSignature,dataEncipherment,keyEncipherment,keyAgreement -ext ExtendedKeyUsage=serverAuth,clientAuth -ext SubjectAlternativeName:c=DNS:localhost,DNS:osx.local,IP:127.0.0.1
    ```

    - `keytool`: Java密钥和证书管理工具。
    - `-v`: 详细输出。
    - `-genkeypair`: 生成密钥对。
    - `-dname "CN=OSX,OU=Fate,O=WB,C=CN"`: 设置证书主题（Distinguished Name）。
    - `-keystore server/identity.jks`: 设置密钥库的文件路径和名称。
    - `-storepass 123456`: 设置密钥库的密码。
    - `-keypass 123456`: 设置生成的密钥对的密码。
    - `-keyalg RSA`: 使用RSA算法生成密钥对。
    - `-keysize 2048`: 设置密钥的大小为2048位。
    - `-alias server`: 设置密钥对的别名。
    - `-validity 3650`: 设置证书的有效期为3650天。
    - `-deststoretype pkcs12`: 指定密钥库的类型为PKCS12。
    - `-ext KeyUsage=digitalSignature,dataEncipherment,keyEncipherment,keyAgreement`: 扩展密钥用途。
    - `-ext ExtendedKeyUsage=serverAuth,clientAuth`: 扩展密钥用途。
    - `-ext SubjectAlternativeName:c=DNS:localhost,DNS:osx.local,IP:127.0.0.1`: 设置主体备用名称，包括DNS和IP地址。(这些主体备用名称的添加允许证书在与这些名称关联的主机或IP地址上使用，而不仅限于使用通用名称（Common Name，CN）字段中指定的主机名。这对于在服务器证书中包含多个主机名或IP地址是很有用的，特别是在使用SSL/TLS进行多主机名（SAN）认证时。)

    此命令用于生成包含服务器证书的密钥库，以便用于安全连接。请确保根据实际需求和环境进行适当的调整。

 2. 密钥库中导出证书，并将其保存为`.cer`文件:

    ```
    keytool -v -exportcert -file server/server.cer -alias server -keystore server/identity.jks -storepass 123456 -rfc
    ```

    - `keytool`: Java密钥和证书管理工具。
    - `-v`: 详细输出。
    - `-exportcert`: 导出证书。
    - `-file server/server.cer`: 指定导出证书的文件路径和名称。
    - `-alias server`: 指定要导出的证书条目的别名。
    - `-keystore server/identity.jks`: 指定密钥库的路径和名称。
    - `-storepass 123456`: 密钥库的密码。
    - `-rfc`: 以RFC 1421格式（Base64编码）输出证书。

    此命令用于从密钥库中导出服务器证书，并将其保存为`.cer`文件。请确保提供正确的密钥库路径、别名和密码，并根据需要更改导出证书的文件路径和名称。

 3. 从证书文件导入证书并将其添加到客户端的信任存储区:

    - ```
      keytool -v -importcert -file server/server.cer -alias server -keystore client/truststore.jks -storepass 123456 -noprompt
      ```

      `keytool`: Java密钥和证书管理工具。

    - `-v`: 详细输出。

    - `-importcert`: 导入证书。

    - `-file server/server.cer`: 指定要导入的证书文件路径和名称。

    - `-alias server`: 指定将证书存储在信任存储区时使用的别名。

    - `-keystore client/truststore.jks`: 指定信任存储区的路径和名称。

    - `-storepass 123456`: 信任存储区的密码。

    - `-noprompt`: 在导入证书时不提示用户确认。

    此命令用于将服务器证书导入到客户端的信任存储区，以建立与服务器的安全连接。确保提供正确的证书文件路径、别名、信任存储区路径和密码，并根据需要更改相关参数。 `-noprompt` 标志确保在导入证书时不需要手动确认。

 4. 生成客户端的密钥对和自签名证书:

    ```
    keytool -v -genkeypair -dname "CN=Suleyman,OU=Altindag,O=Altindag,C=NL" -keystore client/identity.jks -storepass 123456 -keypass 123456 -keyalg RSA -keysize 2048 -alias client -validity 3650 -deststoretype pkcs12 -ext KeyUsage=digitalSignature,dataEncipherment,keyEncipherment,keyAgreement -ext ExtendedKeyUsage=serverAuth,clientAuth
    ```

    - `keytool`: Java密钥和证书管理工具。
    - `-v`: 详细输出。
    - `-genkeypair`: 生成密钥对。
    - `-dname "CN=Suleyman,OU=Altindag,O=Altindag,C=NL"`: 设置证书主题（Distinguished Name，DN）。
    - `-keystore client/identity.jks`: 设置密钥库的文件路径和名称。
    - `-storepass 123456`: 设置密钥库的密码。
    - `-keypass 123456`: 设置生成的密钥对的密码。
    - `-keyalg RSA`: 使用RSA算法生成密钥对。
    - `-keysize 2048`: 设置密钥的大小为2048位。
    - `-alias client`: 设置密钥对的别名。
    - `-validity 3650`: 设置证书的有效期为3650天。
    - `-deststoretype pkcs12`: 指定密钥库的类型为PKCS12。
    - `-ext KeyUsage=digitalSignature,dataEncipherment,keyEncipherment,keyAgreement`: 扩展密钥用途。
    - `-ext ExtendedKeyUsage=serverAuth,clientAuth`: 扩展密钥用途。

    此命令用于生成包含客户端证书的密钥库，以用于安全连接。请确保提供正确的密钥库路径、别名和密码，并根据需要更改其他参数。

 5. 从客户端的密钥库中导出证书，并将其保存为`.cer`文件:

    ```
    keytool -v -exportcert -file client/client.cer -alias client -keystore client/identity.jks -storepass 123456 -rfc
    ```

    - `keytool`: Java密钥和证书管理工具。
    - `-v`: 详细输出。
    - `-exportcert`: 导出证书。
    - `-file client/client.cer`: 指定导出证书的文件路径和名称。
    - `-alias client`: 指定要导出的证书条目的别名。
    - `-keystore client/identity.jks`: 指定密钥库的路径和名称。
    - `-storepass 123456`: 密钥库的密码。
    - `-rfc`: 以RFC 1421格式（Base64编码）输出证书。

    此命令用于从客户端的密钥库中导出客户端证书，并将其保存为`.cer`文件。请确保提供正确的密钥库路径、别名和密码，并根据需要更改导出证书的文件路径和名称。

 6. 从客户端的证书文件中导入证书，并将其添加到服务器的信任存储区:

    ```
    keytool -v -importcert -file client/client.cer -alias client -keystore server/truststore.jks -storepass 123456 -noprompt
    ```

    - `keytool`: Java密钥和证书管理工具。
    - `-v`: 详细输出。
    - `-importcert`: 导入证书。
    - `-file client/client.cer`: 指定要导入的证书文件路径和名称。
    - `-alias client`: 指定将证书存储在信任存储区时使用的别名。
    - `-keystore server/truststore.jks`: 指定信任存储区的路径和名称。
    - `-storepass 123456`: 信任存储区的密码。
    - `-noprompt`: 在导入证书时不提示用户确认。

    此命令用于将客户端证书导入到服务器的信任存储区，以建立与客户端的安全连接。确保提供正确的证书文件路径、别名、信任存储区路径和密码，并根据需要更改相关参数。 `-noprompt` 标志确保在导入证书时不需要手动确认。

#### 完成以上步骤您将生成如下证书：

​			server文件夹包含： identity.jks 、server.cer、truststore.jks； 其中 identity.jks为私钥密码箱，truststore.jks 信任证书密码箱，server.cer为服务器证书（如果使用密码箱，无需配置此文件）。

​			client文件夹包含： identity.jks 、client.cer、truststore.jks；其中 identity.jks为私钥密码箱，truststore.jks 信任证书密码箱，client.cer为客户端证书（如果使用密码箱，无需配置此文件）。

## 2）方式二：单独文件存储私钥、证书、信任证书方式

```
ca.key 
生成CA自己的私钥 root ca.key
# openssl genrsa -out ca.key 2048

ca.crt
根据CA自己的私钥生成自签发的数字证书，该证书里包含CA自己的公钥。
# openssl req -x509 -new -nodes -key ca.key -subj "/CN=osx" -days 5000 -out ca.crt

server.key
服务端的私钥和数字证书（由自CA签发）
生成服务端私钥
# openssl genrsa -out server.key 2048
将其转换成 pkcs8 格式，供java程序使用
#openssl pkcs8 -topk8 -inform PEM -outform PEM -in server.key -out server_pkcs8.key -nocrypt

server.csr 
生成Certificate Sign Request，CSR，证书签名请求。
# openssl req -new -key server.key -subj "/CN=osx" -out server.csr

server.crt
自CA用自己的CA私钥对服务端提交的csr进行签名处理，得到服务端的数字证书server.crt
您的服务器还使用 IP 地址，请根据需要添加：
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 5000 \
    -extfile <(printf "subjectAltName=DNS:grpcpro1.com,IP:your_server_ip")

要对客户端数字证书进行校验，首先客户端需要先有自己的证书。我们以上面的例子为基础，生成客户端的私钥与证书。
client.key
# openssl genrsa -out client.key 2048
将其转换成 pkcs8 格式，供java程序使用
# openssl pkcs8 -topk8 -inform PEM -outform PEM -in client.key -out client_pkcs8.key -nocrypt

client.csr
# openssl req -new -key client.key -subj "/CN=osx" -out client.csr

client.crt
# openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 5000


```

产物：
CA:
私钥文件 ca.key
数字证书 ca.crt

Server:
私钥文件 server.key、server_pkcs8.key（实际配置此格式私钥）
数字证书 server.crt

client:
私钥文件 client.key、client_pkcs8.key（实际配置此格式私钥）
数字证书 client.crt



























