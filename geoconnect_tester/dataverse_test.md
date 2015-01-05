## Test the dataverse API for mapping*
#### (A somewhat convoluted method)

### Create a dataverse with a mappable (public) dataset

This first step uses selenium to add a mappable dataset to the selected Dataverse.

1.  Open ```dataverse_setup_01.py```
  - At the bottom of the file, set the proper ```dataverse_url``` and any user creds.
1.  Save the file.
1.  Run ```python dataverse_setup_01.py```.  Example output:
   ```
Please run with one of the choices below:

 1 - run_user_admin
 2 - run_user_pete

example:
$ python dataverse_setup_01.py 1
```
1.  Run the command again with the proper user number selected.  Example:
   ```
$ python dataverse_setup_01.py 1
```
1.  At this point you should have a browser open with a dataset with a "Map Data" button.

### Get a mapping-related token

Assuming you left off with an open browser, as described in the previous step, do the following:

1.  _Copy_ the "Map Data" link.  The link will be something like:
    - https://dvn-build.hmdc.harvard.edu/api/worldmap/map-it/41/1
1. Manually update the link, changing "map-it" to "map-it-token-only":    
    - https://dvn-build.hmdc.harvard.edu/api/worldmap/map-it-token-only/41/1
1. Copy the link into your still open browser.  With any luck, you will see a JSON response.  
    - Example response: 
    ```javascript
{ "status":"OK",
  "data":
     {"GEOCONNECT_TOKEN":"f32ab9cfc1e6cef6d5f6c9c7d13bb865369dd584d65fabb4b11c6593c38f16c4"}
}
```
1.  Copy the value of ```GEOCONNECT_TOKEN```.  In the example, the value is ```f32ab9cfc1e6cef6d5f6c9c7d13bb865369dd584d65fabb4b11c6593c38f16c4```

### Run the tests

1. Open ```dataverse_test_02.py```
1. At the top of the file, update the following values:
    - ```WORLDMAP_TOKEN_VALUE``` - Use the token value from the previous instructions
    - ```DATAVERSE_SERVER``` - Make sure the server is the same as the one from where you retrieved the token. 
1. At the bottom of the file, under the ```get_suite()``` function, comment/uncomment the tests you would like to run:
   ```python
def get_suite():
    suite = unittest.TestSuite()
    
    suite.addTest(RetrieveFileMetadataTestCase('run_test01_datafile_metadata'))
    suite.addTest(RetrieveFileMetadataTestCase('run_test_02_map_metadata_bad_updates'))
    suite.addTest(RetrieveFileMetadataTestCase('run_test_03_map_metadata_good_update'))
    suite.addTest(RetrieveFileMetadataTestCase('run_test_04_map_metadata_delete'))

    # Deletes token
    #suite.addTest(RetrieveFileMetadataTestCase('run_test_05_delete_token'))
    
    return suite
```
1. Save the file
1. Run ```python dataverse_test_02.py```    

    
