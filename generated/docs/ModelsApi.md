# restclient.ModelsApi

All URIs are relative to *https://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_training_model**](ModelsApi.md#create_training_model) | **POST** /models | 
[**delete_training_model**](ModelsApi.md#delete_training_model) | **DELETE** /models/{id} | 
[**find_training_model**](ModelsApi.md#find_training_model) | **GET** /models/{id} | 
[**get_training_models**](ModelsApi.md#get_training_models) | **GET** /models | 


# **create_training_model**
> InlineResponse201 create_training_model(training_model)



Start a new model training from the corpus specified

### Example 
```python
import time
import restclient
from restclient.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = restclient.ModelsApi()
training_model = restclient.NewTrainingModel() # NewTrainingModel | The model training to begin

try: 
    api_response = api_instance.create_training_model(training_model)
    pprint(api_response)
except ApiException as e:
    print "Exception when calling ModelsApi->create_training_model: %s\n" % e
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **training_model** | [**NewTrainingModel**](NewTrainingModel.md)| The model training to begin | 

### Return type

[**InlineResponse201**](InlineResponse201.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_training_model**
> delete_training_model(id)



Delete the specified training model

### Example 
```python
import time
import restclient
from restclient.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = restclient.ModelsApi()
id = 'id_example' # str | The unique identifier for the training model

try: 
    api_instance.delete_training_model(id)
except ApiException as e:
    print "Exception when calling ModelsApi->delete_training_model: %s\n" % e
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| The unique identifier for the training model | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **find_training_model**
> InlineResponse201 find_training_model(id)



Return detailed information about a training model

### Example 
```python
import time
import restclient
from restclient.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = restclient.ModelsApi()
id = 'id_example' # str | The unique identifier for the training model

try: 
    api_response = api_instance.find_training_model(id)
    pprint(api_response)
except ApiException as e:
    print "Exception when calling ModelsApi->find_training_model: %s\n" % e
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| The unique identifier for the training model | 

### Return type

[**InlineResponse201**](InlineResponse201.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_training_models**
> InlineResponse200 get_training_models()



Returns a list of the models that have been, or are being, trained by the processing driver

### Example 
```python
import time
import restclient
from restclient.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = restclient.ModelsApi()

try: 
    api_response = api_instance.get_training_models()
    pprint(api_response)
except ApiException as e:
    print "Exception when calling ModelsApi->get_training_models: %s\n" % e
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

