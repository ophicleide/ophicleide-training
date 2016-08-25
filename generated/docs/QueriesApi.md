# restclient.QueriesApi

All URIs are relative to *https://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_query**](QueriesApi.md#create_query) | **POST** /queries | 
[**find_query**](QueriesApi.md#find_query) | **GET** /queries/{id} | 
[**get_queries**](QueriesApi.md#get_queries) | **GET** /queries | 


# **create_query**
> InlineResponse2011 create_query(new_query)



Create a new query

### Example 
```python
import time
import restclient
from restclient.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = restclient.QueriesApi()
new_query = restclient.NewQueryRequest() # NewQueryRequest | The query to execute

try: 
    api_response = api_instance.create_query(new_query)
    pprint(api_response)
except ApiException as e:
    print "Exception when calling QueriesApi->create_query: %s\n" % e
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **new_query** | [**NewQueryRequest**](NewQueryRequest.md)| The query to execute | 

### Return type

[**InlineResponse2011**](InlineResponse2011.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **find_query**
> find_query(id)



Return detailed information for the specified query

### Example 
```python
import time
import restclient
from restclient.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = restclient.QueriesApi()
id = 'id_example' # str | The unique identifier for the query

try: 
    api_instance.find_query(id)
except ApiException as e:
    print "Exception when calling QueriesApi->find_query: %s\n" % e
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| The unique identifier for the query | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_queries**
> InlineResponse2001 get_queries()



Return a list of queries submitted to the server

### Example 
```python
import time
import restclient
from restclient.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = restclient.QueriesApi()

try: 
    api_response = api_instance.get_queries()
    pprint(api_response)
except ApiException as e:
    print "Exception when calling QueriesApi->get_queries: %s\n" % e
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

