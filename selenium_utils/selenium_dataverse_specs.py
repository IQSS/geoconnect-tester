


class DataverseInfoChecker:

    REQUIRED_DATAVERSE_ATTRIBUTES = ('name', 'alias', 'description', 'category',)
    OPTIONAL_DATAVERSE_ATTRIBUTES = ('contact_email',)

    @staticmethod
    def is_valid_dataverse_info(dataverse_dict):
        """
        This simply blows up if bad info isgiven
        """
        assert type(dataverse_dict) is dict, "dataverse_dict must be type dict"

        missing_fields = set(DataverseInfoChecker.REQUIRED_DATAVERSE_ATTRIBUTES).difference(dataverse_dict.keys())


        if len(missing_fields) > 0:
            raise KeyError('The dataverse info is missing these fields: %s' % list(missing_fields))

        # Check that required values is not None
        #
        for key_val in DataverseInfoChecker.REQUIRED_DATAVERSE_ATTRIBUTES:
            if dataverse_dict.get(key_val, None) is None:
                raise KeyError('This dataverse info key cannot be None: %s' % key_val)

        # If optional value included, make sure it's not None
        #
        for key_val in DataverseInfoChecker.OPTIONAL_DATAVERSE_ATTRIBUTES:
            if dataverse_dict.has_key(key_val):
                if dataverse_dict.get(key_val, None) is None:
                    raise KeyError('This dataverse info key cannot be None: %s' % key_val)

        return True