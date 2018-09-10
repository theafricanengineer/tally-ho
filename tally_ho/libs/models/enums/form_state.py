from tally_ho.libs.utils.enum import Enum


class FormState(Enum):
    ARCHIVED = 0
    ARCHIVING = 1
    AUDIT = 2
    CLEARANCE = 3
    CORRECTION = 4
    DATA_ENTRY_1 = 5
    DATA_ENTRY_2 = 6
    INTAKE = 7
    QUALITY_CONTROL = 8
    UNSUBMITTED = 9

    _transitions = {
        ARCHIVED: (ARCHIVING, AUDIT),
        ARCHIVING: (QUALITY_CONTROL,),
        AUDIT: (ARCHIVING, CORRECTION, DATA_ENTRY_1, DATA_ENTRY_2,
                ARCHIVED, QUALITY_CONTROL),
        CLEARANCE: (ARCHIVING, INTAKE, UNSUBMITTED, CORRECTION,
                    ARCHIVED, DATA_ENTRY_1, DATA_ENTRY_2, QUALITY_CONTROL),
        CORRECTION: (DATA_ENTRY_2,),
        DATA_ENTRY_1: (AUDIT, CORRECTION, INTAKE, QUALITY_CONTROL),
        DATA_ENTRY_2: (DATA_ENTRY_1,),
        INTAKE: (CLEARANCE, UNSUBMITTED),
        QUALITY_CONTROL: (CORRECTION,),
        UNSUBMITTED: (CLEARANCE, INTAKE),
    }
