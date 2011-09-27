##############
## Mappings ##
##############

# The first item in each tuple is the db representation; the second is the associated Django field name.
# Implemented with getattr(models, [fieldname])
DYN_FIELD_TYPES = (
    ('CHAR', 'CharField'),
    ('FK', 'ForeignKey'),
    ('INT', 'IntegerField'),
    ('FLOA', 'FloatField'),
    ('TEXT', 'TextField')
)

DYN_FIELD_DEFAULTS = {
    'CharField': {
        'max_length': 100,
        'blank': True
    }, 'TextField': {
        'blank': True,
    }, 'IntegerField': {
        'blank': True,
        'null': True
    }, 'FloatField': {
        'blank': True,
        'null': True
    }
}