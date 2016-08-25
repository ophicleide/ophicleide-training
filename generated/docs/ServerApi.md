# restclient.ServerApi

All URIs are relative to *https://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_server_info**](ServerApi.md#get_server_info) | **GET** / | 


# **get_server_info**
> ServerInfo get_server_info()



Returns information about the server version

### Example 
```python
import time
import restclient
from restclient.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = restclient.ServerApi()

try: 
    api_response = api_instance.get_server_info()
    pprint(api_response)
except ApiException as e:
    print "Exception when calling ServerApi->get_server_info: %s\n" % e
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ServerInfo**](ServerInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

