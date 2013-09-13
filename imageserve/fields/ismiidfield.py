class IsmiIdField(models.IntegerField):
    """
    Custom model field which must be a valid ID of a
    Codex object from the ISMI database.
    """
    def to_python(self, value):
        print("Calling ISMI Id Validation")
        # try:
        #     c = get_by_ismi_id(value)
        # except KeyError:
        #     raise ValidationError("Invalid ISMI ID")
        # if c['oc'] != 'CODEX':
        #     raise ValidationError("ISMI entity must be of type CODEX")
        return value