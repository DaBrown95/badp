; Own sprite/palette region: 119 animation records, 24 palette streams, 298 frames.
; Native consumers read flags, width and height at separate byte offsets.
; Pointer closure and contiguous storage do not assert exclusive use or reachability.
.macro UnversionedSpriteFrameShape columns, rows
    .byte columns, rows
.endmacro
UnversionedSpriteResources:
UnversionedSpriteAnimation000:
    ObservedSpriteAnimationHeader $03, $14 ; CONTROL_UNVERSIONED_ANIMATION_000
    .word UnversionedSpriteFrame005 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_000
    .word UnversionedSpriteFrame006
    .word UnversionedSpriteFrame005
UnversionedSpriteAnimation001:
    ObservedSpriteAnimationHeader $05, $0A ; CONTROL_UNVERSIONED_ANIMATION_001
    .word UnversionedSpriteFrame018 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_001
    .word UnversionedSpriteFrame019
    .word UnversionedSpriteFrame018
    .word UnversionedSpriteFrame019
    .word UnversionedSpriteFrame018
UnversionedSpriteAnimation002:
    ObservedSpriteAnimationHeader $04, $06 ; CONTROL_UNVERSIONED_ANIMATION_002
    .word UnversionedSpriteFrame009 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_002
    .word UnversionedSpriteFrame010
    .word UnversionedSpriteFrame011
    .word UnversionedSpriteFrame012
UnversionedSpriteAnimation003:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_003
    .word UnversionedSpriteFrame014 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_003
    .word UnversionedSpriteFrame015
    .word UnversionedSpriteFrame016
UnversionedSpriteAnimation004:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_004
    .word UnversionedSpriteFrame020 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_004
    .word UnversionedSpriteFrame021
UnversionedSpriteAnimation005:
    ObservedSpriteAnimationHeader $02, $14 ; CONTROL_UNVERSIONED_ANIMATION_005
    .word UnversionedSpriteFrame023 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_005
    .word UnversionedSpriteFrame024
UnversionedSpriteAnimation006:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_006
    .word UnversionedSpriteFrame023 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_006
    .word UnversionedSpriteFrame025
UnversionedSpriteAnimation007:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_007
    .word UnversionedSpriteFrame026 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_007
    .word UnversionedSpriteFrame027
    .word UnversionedSpriteFrame028
UnversionedSpriteAnimation008:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_008
    .word UnversionedSpriteFrame029 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_008
    .word UnversionedSpriteFrame031
UnversionedSpriteAnimation009:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_009
    .word UnversionedSpriteFrame029 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_009
    .word UnversionedSpriteFrame030
UnversionedSpriteAnimation010:
    ObservedSpriteAnimationHeader $02, $14 ; CONTROL_UNVERSIONED_ANIMATION_010
    .word UnversionedSpriteFrame032 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_010
    .word UnversionedSpriteFrame035
UnversionedSpriteAnimation011:
    ObservedSpriteAnimationHeader $03, $14 ; CONTROL_UNVERSIONED_ANIMATION_011
    .word UnversionedSpriteFrame032 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_011
    .word UnversionedSpriteFrame033
    .word UnversionedSpriteFrame034
UnversionedSpriteAnimation012:
    ObservedSpriteAnimationHeader $02, $14 ; CONTROL_UNVERSIONED_ANIMATION_012
    .word UnversionedSpriteFrame037 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_012
    .word UnversionedSpriteFrame040
UnversionedSpriteAnimation013:
    ObservedSpriteAnimationHeader $03, $14 ; CONTROL_UNVERSIONED_ANIMATION_013
    .word UnversionedSpriteFrame037 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_013
    .word UnversionedSpriteFrame038
    .word UnversionedSpriteFrame039
UnversionedSpriteAnimation014:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_014
    .word UnversionedSpriteFrame044 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_014
    .word UnversionedSpriteFrame045
UnversionedSpriteAnimation015:
    ObservedSpriteAnimationHeader $06, $03 ; CONTROL_UNVERSIONED_ANIMATION_015
    .word UnversionedSpriteFrame042 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_015
    .word UnversionedSpriteFrame043
    .word UnversionedSpriteFrame042
    .word UnversionedSpriteFrame043
    .word UnversionedSpriteFrame042
    .word UnversionedSpriteFrame043
UnversionedSpriteAnimation016:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_016
    .word UnversionedSpriteFrame046 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_016
    .word UnversionedSpriteFrame047
    .word UnversionedSpriteFrame048
UnversionedSpriteAnimation017:
    ObservedSpriteAnimationHeader $04, $0A ; CONTROL_UNVERSIONED_ANIMATION_017
    .word UnversionedSpriteFrame052 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_017
    .word UnversionedSpriteFrame053
    .word UnversionedSpriteFrame054
    .word UnversionedSpriteFrame053
UnversionedSpriteAnimation018:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_018
    .word UnversionedSpriteFrame056 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_018
    .word UnversionedSpriteFrame057
UnversionedSpriteAnimation019:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_019
    .word UnversionedSpriteFrame055 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_019
    .word UnversionedSpriteFrame056
UnversionedSpriteAnimation020:
    ObservedSpriteAnimationHeader $04, $04 ; CONTROL_UNVERSIONED_ANIMATION_020
    .word UnversionedSpriteFrame001 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_020
    .word UnversionedSpriteFrame002
    .word UnversionedSpriteFrame003
    .word UnversionedSpriteFrame004
UnversionedSpriteAnimation021:
    ObservedSpriteAnimationHeader $06, $0A ; CONTROL_UNVERSIONED_ANIMATION_021
    .word UnversionedSpriteFrame058 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_021
    .word UnversionedSpriteFrame059
    .word UnversionedSpriteFrame060
    .word UnversionedSpriteFrame063
    .word UnversionedSpriteFrame062
    .word UnversionedSpriteFrame062
UnversionedSpriteAnimation022:
    ObservedSpriteAnimationHeader $02, $1E ; CONTROL_UNVERSIONED_ANIMATION_022
    .word UnversionedSpriteFrame060 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_022
    .word UnversionedSpriteFrame061
UnversionedSpriteAnimation023:
    ObservedSpriteAnimationHeader $03, $06 ; CONTROL_UNVERSIONED_ANIMATION_023
    .word UnversionedSpriteFrame058 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_023
    .word UnversionedSpriteFrame059
    .word UnversionedSpriteFrame060
UnversionedSpriteAnimation024:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_024
    .word UnversionedSpriteFrame070 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_024
    .word UnversionedSpriteFrame069
UnversionedSpriteAnimation025:
    ObservedSpriteAnimationHeader $03, $0F ; CONTROL_UNVERSIONED_ANIMATION_025
    .word UnversionedSpriteFrame066 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_025
    .word UnversionedSpriteFrame067
    .word UnversionedSpriteFrame068
UnversionedSpriteAnimation026:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_026
    .word UnversionedSpriteFrame065 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_026
    .word UnversionedSpriteFrame073
UnversionedSpriteAnimation027:
    ObservedSpriteAnimationHeader $03, $05 ; CONTROL_UNVERSIONED_ANIMATION_027
    .word UnversionedSpriteFrame071 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_027
    .word UnversionedSpriteFrame074
    .word UnversionedSpriteFrame075
UnversionedSpriteAnimation028:
    ObservedSpriteAnimationHeader $03, $14 ; CONTROL_UNVERSIONED_ANIMATION_028
    .word UnversionedSpriteFrame065 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_028
    .word UnversionedSpriteFrame064
    .word UnversionedSpriteFrame065
UnversionedSpriteAnimation029:
    ObservedSpriteAnimationHeader $04, $05 ; CONTROL_UNVERSIONED_ANIMATION_029
    .word UnversionedSpriteFrame097 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_029
    .word UnversionedSpriteFrame098
    .word UnversionedSpriteFrame099
    .word UnversionedSpriteFrame097
UnversionedSpriteAnimation030:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_030
    .word UnversionedSpriteFrame100 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_030
    .word UnversionedSpriteFrame101
    .word UnversionedSpriteFrame102
UnversionedSpriteAnimation031:
    ObservedSpriteAnimationHeader $02, $12 ; CONTROL_UNVERSIONED_ANIMATION_031
    .word UnversionedSpriteFrame093 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_031
    .word UnversionedSpriteFrame094
UnversionedSpriteAnimation032:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_032
    .word UnversionedSpriteFrame105 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_032
    .word UnversionedSpriteFrame106
UnversionedSpriteAnimation033:
    ObservedSpriteAnimationHeader $02, $0C ; CONTROL_UNVERSIONED_ANIMATION_033
    .word UnversionedSpriteFrame103 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_033
    .word UnversionedSpriteFrame102
UnversionedSpriteAnimation034:
    ObservedSpriteAnimationHeader $02, $10 ; CONTROL_UNVERSIONED_ANIMATION_034
    .word UnversionedSpriteFrame103 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_034
    .word UnversionedSpriteFrame090
UnversionedSpriteAnimation035:
    ObservedSpriteAnimationHeader $03, $08 ; CONTROL_UNVERSIONED_ANIMATION_035
    .word UnversionedSpriteFrame108 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_035
    .word UnversionedSpriteFrame109
    .word UnversionedSpriteFrame110
UnversionedSpriteAnimation036:
    ObservedSpriteAnimationHeader $04, $08 ; CONTROL_UNVERSIONED_ANIMATION_036
    .word UnversionedSpriteFrame090 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_036
    .word UnversionedSpriteFrame095
    .word UnversionedSpriteFrame096
    .word UnversionedSpriteFrame090
UnversionedSpriteAnimation037:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_037
    .word UnversionedSpriteFrame090 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_037
    .word UnversionedSpriteFrame091
    .word UnversionedSpriteFrame092
UnversionedSpriteAnimation038:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_038
    .word UnversionedSpriteFrame111 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_038
    .word UnversionedSpriteFrame112
UnversionedSpriteAnimation039:
    ObservedSpriteAnimationHeader $13, $06 ; CONTROL_UNVERSIONED_ANIMATION_039
    .word UnversionedSpriteFrame113 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_039
    .word UnversionedSpriteFrame114
    .word UnversionedSpriteFrame115
    .word UnversionedSpriteFrame115
    .word UnversionedSpriteFrame116
    .word UnversionedSpriteFrame117
    .word UnversionedSpriteFrame119
    .word UnversionedSpriteFrame116
    .word UnversionedSpriteFrame115
    .word UnversionedSpriteFrame118
    .word UnversionedSpriteFrame115
    .word UnversionedSpriteFrame118
    .word UnversionedSpriteFrame115
    .word UnversionedSpriteFrame118
    .word UnversionedSpriteFrame115
    .word UnversionedSpriteFrame118
    .word UnversionedSpriteFrame115
    .word UnversionedSpriteFrame114
    .word UnversionedSpriteFrame113
UnversionedSpriteAnimation040:
    ObservedSpriteAnimationHeader $02, $14 ; CONTROL_UNVERSIONED_ANIMATION_040
    .word UnversionedSpriteFrame121 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_040
    .word UnversionedSpriteFrame122
UnversionedSpriteAnimation041:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_041
    .word UnversionedSpriteFrame124 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_041
    .word UnversionedSpriteFrame125
UnversionedSpriteAnimation042:
    ObservedSpriteAnimationHeader $02, $14 ; CONTROL_UNVERSIONED_ANIMATION_042
    .word UnversionedSpriteFrame120 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_042
    .word UnversionedSpriteFrame123
UnversionedSpriteAnimation043:
    ObservedSpriteAnimationHeader $02, $1E ; CONTROL_UNVERSIONED_ANIMATION_043
    .word UnversionedSpriteFrame128 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_043
    .word UnversionedSpriteFrame126
UnversionedSpriteAnimation044:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_044
    .word UnversionedSpriteFrame126 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_044
    .word UnversionedSpriteFrame127
UnversionedSpriteAnimation045:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_045
    .word UnversionedSpriteFrame129 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_045
    .word UnversionedSpriteFrame130
UnversionedSpriteAnimation046:
    ObservedSpriteAnimationHeader $03, $07 ; CONTROL_UNVERSIONED_ANIMATION_046
    .word UnversionedSpriteFrame131 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_046
    .word UnversionedSpriteFrame132
    .word UnversionedSpriteFrame133
UnversionedSpriteAnimation047:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_047
    .word UnversionedSpriteFrame141 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_047
    .word UnversionedSpriteFrame144
UnversionedSpriteAnimation048:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_048
    .word UnversionedSpriteFrame141 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_048
    .word UnversionedSpriteFrame142
    .word UnversionedSpriteFrame143
UnversionedSpriteAnimation049:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_049
    .word UnversionedSpriteFrame134 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_049
    .word UnversionedSpriteFrame135
    .word UnversionedSpriteFrame136
UnversionedSpriteAnimation050:
    ObservedSpriteAnimationHeader $02, $0F ; CONTROL_UNVERSIONED_ANIMATION_050
    .word UnversionedSpriteFrame137 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_050
    .word UnversionedSpriteFrame138
UnversionedSpriteAnimation051:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_051
    .word UnversionedSpriteFrame152 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_051
    .word UnversionedSpriteFrame153
UnversionedSpriteAnimation052:
    ObservedSpriteAnimationHeader $02, $31 ; CONTROL_UNVERSIONED_ANIMATION_052
    .word UnversionedSpriteFrame145 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_052
    .word UnversionedSpriteFrame151
UnversionedSpriteAnimation053:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_053
    .word UnversionedSpriteFrame148 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_053
    .word UnversionedSpriteFrame149
    .word UnversionedSpriteFrame150
UnversionedSpriteAnimation054:
    ObservedSpriteAnimationHeader $07, $0F ; CONTROL_UNVERSIONED_ANIMATION_054
    .word UnversionedSpriteFrame145 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_054
    .word UnversionedSpriteFrame146
    .word UnversionedSpriteFrame147
    .word UnversionedSpriteFrame146
    .word UnversionedSpriteFrame147
    .word UnversionedSpriteFrame146
    .word UnversionedSpriteFrame145
UnversionedSpriteAnimation055:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_055
    .word UnversionedSpriteFrame148 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_055
    .word UnversionedSpriteFrame150
UnversionedSpriteAnimation056:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_056
    .word UnversionedSpriteFrame161 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_056
    .word UnversionedSpriteFrame162
UnversionedSpriteAnimation057:
    ObservedSpriteAnimationHeader $02, $31 ; CONTROL_UNVERSIONED_ANIMATION_057
    .word UnversionedSpriteFrame154 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_057
    .word UnversionedSpriteFrame160
UnversionedSpriteAnimation058:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_058
    .word UnversionedSpriteFrame157 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_058
    .word UnversionedSpriteFrame158
    .word UnversionedSpriteFrame159
UnversionedSpriteAnimation059:
    ObservedSpriteAnimationHeader $06, $0F ; CONTROL_UNVERSIONED_ANIMATION_059
    .word UnversionedSpriteFrame154 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_059
    .word UnversionedSpriteFrame155
    .word UnversionedSpriteFrame156
    .word UnversionedSpriteFrame155
    .word UnversionedSpriteFrame156
    .word UnversionedSpriteFrame155
UnversionedSpriteAnimation060:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_060
    .word UnversionedSpriteFrame157 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_060
    .word UnversionedSpriteFrame159
UnversionedSpriteAnimation061:
    ObservedSpriteAnimationHeader $02, $1E ; CONTROL_UNVERSIONED_ANIMATION_061
    .word UnversionedSpriteFrame163 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_061
    .word UnversionedSpriteFrame164
UnversionedSpriteAnimation062:
    ObservedSpriteAnimationHeader $02, $05 ; CONTROL_UNVERSIONED_ANIMATION_062
    .word UnversionedSpriteFrame165 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_062
    .word UnversionedSpriteFrame166
UnversionedSpriteAnimation063:
    ObservedSpriteAnimationHeader $02, $14 ; CONTROL_UNVERSIONED_ANIMATION_063
    .word UnversionedSpriteFrame167 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_063
    .word UnversionedSpriteFrame170
UnversionedSpriteAnimation064:
    ObservedSpriteAnimationHeader $03, $14 ; CONTROL_UNVERSIONED_ANIMATION_064
    .word UnversionedSpriteFrame167 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_064
    .word UnversionedSpriteFrame168
    .word UnversionedSpriteFrame169
UnversionedSpriteAnimation065:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_065
    .word UnversionedSpriteFrame171 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_065
    .word UnversionedSpriteFrame172
    .word UnversionedSpriteFrame173
UnversionedSpriteAnimation066:
    ObservedSpriteAnimationHeader $02, $1C ; CONTROL_UNVERSIONED_ANIMATION_066
    .word UnversionedSpriteFrame174 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_066
    .word UnversionedSpriteFrame175
UnversionedSpriteAnimation067:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_067
    .word UnversionedSpriteFrame174 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_067
    .word UnversionedSpriteFrame176
UnversionedSpriteAnimation068:
    ObservedSpriteAnimationHeader $02, $09 ; CONTROL_UNVERSIONED_ANIMATION_068
    .word UnversionedSpriteFrame177 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_068
    .word UnversionedSpriteFrame180
UnversionedSpriteAnimation069:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_069
    .word UnversionedSpriteFrame177 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_069
    .word UnversionedSpriteFrame178
    .word UnversionedSpriteFrame179
UnversionedSpriteAnimation070:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_070
    .word UnversionedSpriteFrame186 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_070
    .word UnversionedSpriteFrame187
UnversionedSpriteAnimation071:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_071
    .word UnversionedSpriteFrame184 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_071
    .word UnversionedSpriteFrame185
    .word UnversionedSpriteFrame183
UnversionedSpriteAnimation072:
    ObservedSpriteAnimationHeader $02, $14 ; CONTROL_UNVERSIONED_ANIMATION_072
    .word UnversionedSpriteFrame197 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_072
    .word UnversionedSpriteFrame199
UnversionedSpriteAnimation073:
    ObservedSpriteAnimationHeader $02, $14 ; CONTROL_UNVERSIONED_ANIMATION_073
    .word UnversionedSpriteFrame197 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_073
    .word UnversionedSpriteFrame198
UnversionedSpriteAnimation074:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_074
    .word UnversionedSpriteFrame194 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_074
    .word UnversionedSpriteFrame195
    .word UnversionedSpriteFrame196
UnversionedSpriteAnimation075:
    ObservedSpriteAnimationHeader $03, $14 ; CONTROL_UNVERSIONED_ANIMATION_075
    .word UnversionedSpriteFrame191 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_075
    .word UnversionedSpriteFrame192
    .word UnversionedSpriteFrame191
UnversionedSpriteAnimation076:
    ObservedSpriteAnimationHeader $02, $14 ; CONTROL_UNVERSIONED_ANIMATION_076
    .word UnversionedSpriteFrame191 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_076
    .word UnversionedSpriteFrame193
UnversionedSpriteAnimation077:
    ObservedSpriteAnimationHeader $03, $05 ; CONTROL_UNVERSIONED_ANIMATION_077
    .word UnversionedSpriteFrame188 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_077
    .word UnversionedSpriteFrame189
    .word UnversionedSpriteFrame190
UnversionedSpriteAnimation078:
    ObservedSpriteAnimationHeader $0E, $02 ; CONTROL_UNVERSIONED_ANIMATION_078
    .word UnversionedSpriteFrame200 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_078
    .word UnversionedSpriteFrame201
    .word UnversionedSpriteFrame201
    .word UnversionedSpriteFrame201
    .word UnversionedSpriteFrame202
    .word UnversionedSpriteFrame203
    .word UnversionedSpriteFrame202
    .word UnversionedSpriteFrame203
    .word UnversionedSpriteFrame202
    .word UnversionedSpriteFrame203
    .word UnversionedSpriteFrame202
    .word UnversionedSpriteFrame203
    .word UnversionedSpriteFrame201
    .word UnversionedSpriteFrame200
UnversionedSpriteAnimation079:
    ObservedSpriteAnimationHeader $02, $04 ; CONTROL_UNVERSIONED_ANIMATION_079
    .word UnversionedSpriteFrame204 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_079
    .word UnversionedSpriteFrame206
UnversionedSpriteAnimation080:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_080
    .word UnversionedSpriteFrame204 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_080
    .word UnversionedSpriteFrame205
UnversionedSpriteAnimation081:
    ObservedSpriteAnimationHeader $04, $06 ; CONTROL_UNVERSIONED_ANIMATION_081
    .word UnversionedSpriteFrame212 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_081
    .word UnversionedSpriteFrame214
    .word UnversionedSpriteFrame213
    .word UnversionedSpriteFrame214
UnversionedSpriteAnimation082:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_082
    .word UnversionedSpriteFrame207 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_082
    .word UnversionedSpriteFrame208
    .word UnversionedSpriteFrame209
UnversionedSpriteAnimation083:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_083
    .word UnversionedSpriteFrame210 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_083
    .word UnversionedSpriteFrame211
UnversionedSpriteAnimation084:
    ObservedSpriteAnimationHeader $04, $06 ; CONTROL_UNVERSIONED_ANIMATION_084
    .word UnversionedSpriteFrame216 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_084
    .word UnversionedSpriteFrame217
    .word UnversionedSpriteFrame218
    .word UnversionedSpriteFrame217
UnversionedSpriteAnimation085:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_085
    .word UnversionedSpriteFrame216 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_085
    .word UnversionedSpriteFrame219
UnversionedSpriteAnimation086:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_086
    .word UnversionedSpriteFrame216 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_086
    .word UnversionedSpriteFrame217
UnversionedSpriteAnimation087:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_087
    .word UnversionedSpriteFrame224 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_087
    .word UnversionedSpriteFrame226
UnversionedSpriteAnimation088:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_088
    .word UnversionedSpriteFrame224 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_088
    .word UnversionedSpriteFrame225
UnversionedSpriteAnimation089:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_089
    .word UnversionedSpriteFrame220 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_089
    .word UnversionedSpriteFrame221
    .word UnversionedSpriteFrame222
UnversionedSpriteAnimation090:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_090
    .word UnversionedSpriteFrame227 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_090
    .word UnversionedSpriteFrame228
    .word UnversionedSpriteFrame229
UnversionedSpriteAnimation091:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_091
    .word UnversionedSpriteFrame233 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_091
    .word UnversionedSpriteFrame232
UnversionedSpriteAnimation092:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_092
    .word UnversionedSpriteFrame234 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_092
    .word UnversionedSpriteFrame235
UnversionedSpriteAnimation093:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_093
    .word UnversionedSpriteFrame236 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_093
    .word UnversionedSpriteFrame237
UnversionedSpriteAnimation094:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_094
    .word UnversionedSpriteFrame050 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_094
    .word UnversionedSpriteFrame231
    .word UnversionedSpriteFrame232
UnversionedSpriteAnimation095:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_095
    .word UnversionedSpriteFrame242 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_095
    .word UnversionedSpriteFrame243
UnversionedSpriteAnimation096:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_096
    .word UnversionedSpriteFrame244 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_096
    .word UnversionedSpriteFrame245
    .word UnversionedSpriteFrame246
UnversionedSpriteAnimation097:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_097
    .word UnversionedSpriteFrame247 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_097
    .word UnversionedSpriteFrame244
UnversionedSpriteAnimation098:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_098
    .word UnversionedSpriteFrame244 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_098
    .word UnversionedSpriteFrame248
    .word UnversionedSpriteFrame249
UnversionedSpriteAnimation099:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_099
    .word UnversionedSpriteFrame239 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_099
    .word UnversionedSpriteFrame240
    .word UnversionedSpriteFrame241
UnversionedSpriteAnimation100:
    ObservedSpriteAnimationHeader $06, $0A ; CONTROL_UNVERSIONED_ANIMATION_100
    .word UnversionedSpriteFrame250 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_100
    .word UnversionedSpriteFrame251
    .word UnversionedSpriteFrame252
    .word UnversionedSpriteFrame253
    .word UnversionedSpriteFrame254
    .word UnversionedSpriteFrame255
UnversionedSpriteAnimation101:
    ObservedSpriteAnimationHeader $02, $04 ; CONTROL_UNVERSIONED_ANIMATION_101
    .word UnversionedSpriteFrame256 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_101
    .word UnversionedSpriteFrame258
UnversionedSpriteAnimation102:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_102
    .word UnversionedSpriteFrame256 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_102
    .word UnversionedSpriteFrame257
UnversionedSpriteAnimation103:
    ObservedSpriteAnimationHeader $04, $0A ; CONTROL_UNVERSIONED_ANIMATION_103
    .word UnversionedSpriteFrame264 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_103
    .word UnversionedSpriteFrame265
    .word UnversionedSpriteFrame263
    .word UnversionedSpriteFrame265
UnversionedSpriteAnimation104:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_104
    .word UnversionedSpriteFrame260 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_104
    .word UnversionedSpriteFrame261
    .word UnversionedSpriteFrame262
UnversionedSpriteAnimation105:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_105
    .word UnversionedSpriteFrame259 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_105
    .word UnversionedSpriteFrame256
UnversionedSpriteAnimation106:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_106
    .word UnversionedSpriteFrame266 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_106
    .word UnversionedSpriteFrame267
    .word UnversionedSpriteFrame268
UnversionedSpriteAnimation107:
    ObservedSpriteAnimationHeader $04, $04 ; CONTROL_UNVERSIONED_ANIMATION_107
    .word UnversionedSpriteFrame270 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_107
    .word UnversionedSpriteFrame271
    .word UnversionedSpriteFrame272
    .word UnversionedSpriteFrame271
UnversionedSpriteAnimation108:
    ObservedSpriteAnimationHeader $02, $0F ; CONTROL_UNVERSIONED_ANIMATION_108
    .word UnversionedSpriteFrame273 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_108
    .word UnversionedSpriteFrame274
UnversionedSpriteAnimation109:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_109
    .word UnversionedSpriteFrame278 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_109
    .word UnversionedSpriteFrame280
UnversionedSpriteAnimation110:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_110
    .word UnversionedSpriteFrame278 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_110
    .word UnversionedSpriteFrame276
    .word UnversionedSpriteFrame277
UnversionedSpriteAnimation111:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_111
    .word UnversionedSpriteFrame275 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_111
    .word UnversionedSpriteFrame276
    .word UnversionedSpriteFrame279
UnversionedSpriteAnimation112:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_112
    .word UnversionedSpriteFrame281 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_112
    .word UnversionedSpriteFrame285
    .word UnversionedSpriteFrame281
UnversionedSpriteAnimation113:
    ObservedSpriteAnimationHeader $02, $1E ; CONTROL_UNVERSIONED_ANIMATION_113
    .word UnversionedSpriteFrame281 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_113
    .word UnversionedSpriteFrame282
UnversionedSpriteAnimation114:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_114
    .word UnversionedSpriteFrame286 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_114
    .word UnversionedSpriteFrame287
UnversionedSpriteAnimation115:
    ObservedSpriteAnimationHeader $02, $1E ; CONTROL_UNVERSIONED_ANIMATION_115
    .word UnversionedSpriteFrame283 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_115
    .word UnversionedSpriteFrame284
UnversionedSpriteAnimation116:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_116
    .word UnversionedSpriteFrame289 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_116
    .word UnversionedSpriteFrame290
    .word UnversionedSpriteFrame289
UnversionedSpriteAnimation117:
    ObservedSpriteAnimationHeader $03, $0A ; CONTROL_UNVERSIONED_ANIMATION_117
    .word UnversionedSpriteFrame292 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_117
    .word UnversionedSpriteFrame293
    .word UnversionedSpriteFrame294
UnversionedSpriteAnimation118:
    ObservedSpriteAnimationHeader $02, $0A ; CONTROL_UNVERSIONED_ANIMATION_118
    .word UnversionedSpriteFrame295 ; CONTROL_UNVERSIONED_ANIMATION_POINTER_118
    .word UnversionedSpriteFrame296
.assert * = $B70E, error, "unversioned animation directory end"
UnversionedPalette00:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_00
    .incbin "unversioned-palette-00.bin"
UnversionedPalette01:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_01
    .incbin "unversioned-palette-01.bin"
UnversionedPalette02:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_02
    .incbin "unversioned-palette-02.bin"
UnversionedPalette03:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_03
    .incbin "unversioned-palette-03.bin"
UnversionedPalette04:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_04
    .incbin "unversioned-palette-04.bin"
UnversionedPalette05:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_05
    .incbin "unversioned-palette-05.bin"
UnversionedPalette06:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_06
    .incbin "unversioned-palette-06.bin"
UnversionedPalette07:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_07
    .incbin "unversioned-palette-07.bin"
UnversionedPalette08:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_08
    .incbin "unversioned-palette-08.bin"
UnversionedPalette09:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_09
    .incbin "unversioned-palette-09.bin"
UnversionedPalette10:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_10
    .incbin "unversioned-palette-10.bin"
UnversionedPalette11:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_11
    .incbin "unversioned-palette-11.bin"
UnversionedPalette12:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_12
    .incbin "unversioned-palette-12.bin"
UnversionedPalette13:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_13
    .incbin "unversioned-palette-13.bin"
UnversionedPalette14:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_14
    .incbin "unversioned-palette-14.bin"
UnversionedPalette15:
    PaletteStreamHeader $01, $03, $0A ; CONTROL_UNVERSIONED_PALETTE_15
    .incbin "unversioned-palette-15.bin"
UnversionedPalette16:
    PaletteStreamHeader $01, $03, $0A ; CONTROL_UNVERSIONED_PALETTE_16
    .incbin "unversioned-palette-16.bin"
UnversionedPalette17:
    PaletteStreamHeader $01, $03, $0A ; CONTROL_UNVERSIONED_PALETTE_17
    .incbin "unversioned-palette-17.bin"
UnversionedPalette18:
    PaletteStreamHeader $01, $03, $0A ; CONTROL_UNVERSIONED_PALETTE_18
    .incbin "unversioned-palette-18.bin"
UnversionedPalette19:
    PaletteStreamHeader $01, $03, $0A ; CONTROL_UNVERSIONED_PALETTE_19
    .incbin "unversioned-palette-19.bin"
UnversionedPalette20:
    PaletteStreamHeader $01, $03, $0A ; CONTROL_UNVERSIONED_PALETTE_20
    .incbin "unversioned-palette-20.bin"
UnversionedPalette21:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_21
    .incbin "unversioned-palette-21.bin"
UnversionedPalette22:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_22
    .incbin "unversioned-palette-22.bin"
UnversionedPalette23:
    PaletteStreamHeader $00, $00, $00 ; CONTROL_UNVERSIONED_PALETTE_23
    .incbin "unversioned-palette-23.bin"
.assert * = $B906, error, "unversioned palette region end"
UnversionedSpriteFrame000:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_000
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_000
    .incbin "unversioned-sprite-000.bin"
UnversionedSpriteFrame001:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_001
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_001
    .incbin "unversioned-sprite-001.bin"
UnversionedSpriteFrame002:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_002
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_002
    .incbin "unversioned-sprite-002.bin"
UnversionedSpriteFrame003:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_003
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_003
    .incbin "unversioned-sprite-003.bin"
UnversionedSpriteFrame004:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_004
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_004
    .incbin "unversioned-sprite-004.bin"
UnversionedSpriteFrame005:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_005
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_005
    .incbin "unversioned-sprite-005.bin"
UnversionedSpriteFrame006:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_006
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_006
    .incbin "unversioned-sprite-006.bin"
UnversionedSpriteFrame007:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_007
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_007
    .incbin "unversioned-sprite-007.bin"
UnversionedSpriteFrame008:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_008
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_008
    .incbin "unversioned-sprite-008.bin"
UnversionedSpriteFrame009:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_009
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_009
    .incbin "unversioned-sprite-009.bin"
UnversionedSpriteFrame010:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_010
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_010
    .incbin "unversioned-sprite-010.bin"
UnversionedSpriteFrame011:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_011
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_011
    .incbin "unversioned-sprite-011.bin"
UnversionedSpriteFrame012:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_012
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_012
    .incbin "unversioned-sprite-012.bin"
UnversionedSpriteFrame013:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_013
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_013
    .incbin "unversioned-sprite-013.bin"
UnversionedSpriteFrame014:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_014
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_014
    .incbin "unversioned-sprite-014.bin"
UnversionedSpriteFrame015:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_015
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_015
    .incbin "unversioned-sprite-015.bin"
UnversionedSpriteFrame016:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_016
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_016
    .incbin "unversioned-sprite-016.bin"
UnversionedSpriteFrame017:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_017
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_017
    .incbin "unversioned-sprite-017.bin"
UnversionedSpriteFrame018:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_018
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_018
    .incbin "unversioned-sprite-018.bin"
UnversionedSpriteFrame019:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_019
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_019
    .incbin "unversioned-sprite-019.bin"
UnversionedSpriteFrame020:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_020
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_020
    .incbin "unversioned-sprite-020.bin"
UnversionedSpriteFrame021:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_021
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_021
    .incbin "unversioned-sprite-021.bin"
UnversionedSpriteFrame022:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_022
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_022
    .incbin "unversioned-sprite-022.bin"
UnversionedSpriteFrame023:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_023
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_023
    .incbin "unversioned-sprite-023.bin"
UnversionedSpriteFrame024:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_024
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_024
    .incbin "unversioned-sprite-024.bin"
UnversionedSpriteFrame025:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_025
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_025
    .incbin "unversioned-sprite-025.bin"
UnversionedSpriteFrame026:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_026
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_026
    .incbin "unversioned-sprite-026.bin"
UnversionedSpriteFrame027:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_027
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_027
    .incbin "unversioned-sprite-027.bin"
UnversionedSpriteFrame028:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_028
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_028
    .incbin "unversioned-sprite-028.bin"
UnversionedSpriteFrame029:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_029
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_029
    .incbin "unversioned-sprite-029.bin"
UnversionedSpriteFrame030:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_030
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_030
    .incbin "unversioned-sprite-030.bin"
UnversionedSpriteFrame031:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_031
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_031
    .incbin "unversioned-sprite-031.bin"
UnversionedSpriteFrame032:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_032
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_032
    .incbin "unversioned-sprite-032.bin"
UnversionedSpriteFrame033:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_033
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_033
    .incbin "unversioned-sprite-033.bin"
UnversionedSpriteFrame034:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_034
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_034
    .incbin "unversioned-sprite-034.bin"
UnversionedSpriteFrame035:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_035
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_035
    .incbin "unversioned-sprite-035.bin"
UnversionedSpriteFrame036:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_036
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_036
    .incbin "unversioned-sprite-036.bin"
UnversionedSpriteFrame037:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_037
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_037
    .incbin "unversioned-sprite-037.bin"
UnversionedSpriteFrame038:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_038
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_038
    .incbin "unversioned-sprite-038.bin"
UnversionedSpriteFrame039:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_039
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_039
    .incbin "unversioned-sprite-039.bin"
UnversionedSpriteFrame040:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_040
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_040
    .incbin "unversioned-sprite-040.bin"
UnversionedSpriteFrame041:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_041
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_041
    .incbin "unversioned-sprite-041.bin"
UnversionedSpriteFrame042:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_042
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_042
    .incbin "unversioned-sprite-042.bin"
UnversionedSpriteFrame043:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_043
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_043
    .incbin "unversioned-sprite-043.bin"
UnversionedSpriteFrame044:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_044
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_044
    .incbin "unversioned-sprite-044.bin"
UnversionedSpriteFrame045:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_045
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_045
    .incbin "unversioned-sprite-045.bin"
UnversionedSpriteFrame046:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_046
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_046
    .incbin "unversioned-sprite-046.bin"
UnversionedSpriteFrame047:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_047
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_047
    .incbin "unversioned-sprite-047.bin"
UnversionedSpriteFrame048:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_048
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_048
    .incbin "unversioned-sprite-048.bin"
UnversionedSpriteFrame049:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_049
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_049
    .incbin "unversioned-sprite-049.bin"
UnversionedSpriteFrame050:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_050
    UnversionedSpriteFrameShape $01, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_050
    .incbin "unversioned-sprite-050.bin"
UnversionedSpriteFrame051:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_051
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_051
    .incbin "unversioned-sprite-051.bin"
UnversionedSpriteFrame052:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_052
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_052
    .incbin "unversioned-sprite-052.bin"
UnversionedSpriteFrame053:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_053
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_053
    .incbin "unversioned-sprite-053.bin"
UnversionedSpriteFrame054:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_054
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_054
    .incbin "unversioned-sprite-054.bin"
UnversionedSpriteFrame055:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_055
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_055
    .incbin "unversioned-sprite-055.bin"
UnversionedSpriteFrame056:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_056
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_056
    .incbin "unversioned-sprite-056.bin"
UnversionedSpriteFrame057:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_057
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_057
    .incbin "unversioned-sprite-057.bin"
UnversionedSpriteFrame058:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_058
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_058
    .incbin "unversioned-sprite-058.bin"
UnversionedSpriteFrame059:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_059
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_059
    .incbin "unversioned-sprite-059.bin"
UnversionedSpriteFrame060:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_060
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_060
    .incbin "unversioned-sprite-060.bin"
UnversionedSpriteFrame061:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_061
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_061
    .incbin "unversioned-sprite-061.bin"
UnversionedSpriteFrame062:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_062
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_062
    .incbin "unversioned-sprite-062.bin"
UnversionedSpriteFrame063:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_063
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_063
    .incbin "unversioned-sprite-063.bin"
UnversionedSpriteFrame064:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_064
    UnversionedSpriteFrameShape $04, $04 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_064
    .incbin "unversioned-sprite-064.bin"
UnversionedSpriteFrame065:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_065
    UnversionedSpriteFrameShape $04, $04 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_065
    .incbin "unversioned-sprite-065.bin"
UnversionedSpriteFrame066:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_066
    UnversionedSpriteFrameShape $04, $04 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_066
    .incbin "unversioned-sprite-066.bin"
UnversionedSpriteFrame067:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_067
    UnversionedSpriteFrameShape $04, $04 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_067
    .incbin "unversioned-sprite-067.bin"
UnversionedSpriteFrame068:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_068
    UnversionedSpriteFrameShape $04, $04 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_068
    .incbin "unversioned-sprite-068.bin"
UnversionedSpriteFrame069:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_069
    UnversionedSpriteFrameShape $04, $04 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_069
    .incbin "unversioned-sprite-069.bin"
UnversionedSpriteFrame070:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_070
    UnversionedSpriteFrameShape $04, $04 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_070
    .incbin "unversioned-sprite-070.bin"
UnversionedSpriteFrame071:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_071
    UnversionedSpriteFrameShape $06, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_071
    .incbin "unversioned-sprite-071.bin"
UnversionedSpriteFrame072:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_072
    UnversionedSpriteFrameShape $06, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_072
    .incbin "unversioned-sprite-072.bin"
UnversionedSpriteFrame073:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_073
    UnversionedSpriteFrameShape $04, $04 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_073
    .incbin "unversioned-sprite-073.bin"
UnversionedSpriteFrame074:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_074
    UnversionedSpriteFrameShape $06, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_074
    .incbin "unversioned-sprite-074.bin"
UnversionedSpriteFrame075:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_075
    UnversionedSpriteFrameShape $06, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_075
    .incbin "unversioned-sprite-075.bin"
UnversionedSpriteFrame076:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_076
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_076
    .incbin "unversioned-sprite-076.bin"
UnversionedSpriteFrame077:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_077
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_077
    .incbin "unversioned-sprite-077.bin"
UnversionedSpriteFrame078:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_078
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_078
    .incbin "unversioned-sprite-078.bin"
UnversionedSpriteFrame079:
    ObservedSpriteOamFlags $3B, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_079
    UnversionedSpriteFrameShape $01, $05 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_079
    .incbin "unversioned-sprite-079.bin"
UnversionedSpriteFrame080:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_080
    UnversionedSpriteFrameShape $01, $05 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_080
    .incbin "unversioned-sprite-080.bin"
UnversionedSpriteFrame081:
    ObservedSpriteOamFlags $3B, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_081
    UnversionedSpriteFrameShape $01, $05 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_081
    .incbin "unversioned-sprite-081.bin"
UnversionedSpriteFrame082:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_082
    UnversionedSpriteFrameShape $01, $05 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_082
    .incbin "unversioned-sprite-082.bin"
UnversionedSpriteFrame083:
    ObservedSpriteOamFlags $3B, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_083
    UnversionedSpriteFrameShape $01, $05 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_083
    .incbin "unversioned-sprite-083.bin"
UnversionedSpriteFrame084:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_084
    UnversionedSpriteFrameShape $01, $05 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_084
    .incbin "unversioned-sprite-084.bin"
UnversionedSpriteFrame085:
    ObservedSpriteOamFlags $3B, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_085
    UnversionedSpriteFrameShape $01, $05 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_085
    .incbin "unversioned-sprite-085.bin"
UnversionedSpriteFrame086:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_086
    UnversionedSpriteFrameShape $01, $05 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_086
    .incbin "unversioned-sprite-086.bin"
UnversionedSpriteFrame087:
    ObservedSpriteOamFlags $3B, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_087
    UnversionedSpriteFrameShape $01, $05 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_087
    .incbin "unversioned-sprite-087.bin"
UnversionedSpriteFrame088:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_088
    UnversionedSpriteFrameShape $01, $05 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_088
    .incbin "unversioned-sprite-088.bin"
UnversionedSpriteFrame089:
    ObservedSpriteOamFlags $3B, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_089
    UnversionedSpriteFrameShape $01, $05 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_089
    .incbin "unversioned-sprite-089.bin"
UnversionedSpriteFrame090:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_090
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_090
    .incbin "unversioned-sprite-090.bin"
UnversionedSpriteFrame091:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_091
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_091
    .incbin "unversioned-sprite-091.bin"
UnversionedSpriteFrame092:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_092
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_092
    .incbin "unversioned-sprite-092.bin"
UnversionedSpriteFrame093:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_093
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_093
    .incbin "unversioned-sprite-093.bin"
UnversionedSpriteFrame094:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_094
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_094
    .incbin "unversioned-sprite-094.bin"
UnversionedSpriteFrame095:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_095
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_095
    .incbin "unversioned-sprite-095.bin"
UnversionedSpriteFrame096:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_096
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_096
    .incbin "unversioned-sprite-096.bin"
UnversionedSpriteFrame097:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_097
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_097
    .incbin "unversioned-sprite-097.bin"
UnversionedSpriteFrame098:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_098
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_098
    .incbin "unversioned-sprite-098.bin"
UnversionedSpriteFrame099:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_099
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_099
    .incbin "unversioned-sprite-099.bin"
UnversionedSpriteFrame100:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_100
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_100
    .incbin "unversioned-sprite-100.bin"
UnversionedSpriteFrame101:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_101
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_101
    .incbin "unversioned-sprite-101.bin"
UnversionedSpriteFrame102:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_102
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_102
    .incbin "unversioned-sprite-102.bin"
UnversionedSpriteFrame103:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_103
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_103
    .incbin "unversioned-sprite-103.bin"
UnversionedSpriteFrame104:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_104
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_104
    .incbin "unversioned-sprite-104.bin"
UnversionedSpriteFrame105:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_105
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_105
    .incbin "unversioned-sprite-105.bin"
UnversionedSpriteFrame106:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_106
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_106
    .incbin "unversioned-sprite-106.bin"
UnversionedSpriteFrame107:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_107
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_107
    .incbin "unversioned-sprite-107.bin"
UnversionedSpriteFrame108:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_108
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_108
    .incbin "unversioned-sprite-108.bin"
UnversionedSpriteFrame109:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_109
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_109
    .incbin "unversioned-sprite-109.bin"
UnversionedSpriteFrame110:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_110
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_110
    .incbin "unversioned-sprite-110.bin"
UnversionedSpriteFrame111:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_111
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_111
    .incbin "unversioned-sprite-111.bin"
UnversionedSpriteFrame112:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_112
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_112
    .incbin "unversioned-sprite-112.bin"
UnversionedSpriteFrame113:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_113
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_113
    .incbin "unversioned-sprite-113.bin"
UnversionedSpriteFrame114:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_114
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_114
    .incbin "unversioned-sprite-114.bin"
UnversionedSpriteFrame115:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_115
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_115
    .incbin "unversioned-sprite-115.bin"
UnversionedSpriteFrame116:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_116
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_116
    .incbin "unversioned-sprite-116.bin"
UnversionedSpriteFrame117:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_117
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_117
    .incbin "unversioned-sprite-117.bin"
UnversionedSpriteFrame118:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_118
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_118
    .incbin "unversioned-sprite-118.bin"
UnversionedSpriteFrame119:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_119
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_119
    .incbin "unversioned-sprite-119.bin"
UnversionedSpriteFrame120:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_120
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_120
    .incbin "unversioned-sprite-120.bin"
UnversionedSpriteFrame121:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_121
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_121
    .incbin "unversioned-sprite-121.bin"
UnversionedSpriteFrame122:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_122
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_122
    .incbin "unversioned-sprite-122.bin"
UnversionedSpriteFrame123:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_123
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_123
    .incbin "unversioned-sprite-123.bin"
UnversionedSpriteFrame124:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_124
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_124
    .incbin "unversioned-sprite-124.bin"
UnversionedSpriteFrame125:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_125
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_125
    .incbin "unversioned-sprite-125.bin"
UnversionedSpriteFrame126:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_126
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_126
    .incbin "unversioned-sprite-126.bin"
UnversionedSpriteFrame127:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_127
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_127
    .incbin "unversioned-sprite-127.bin"
UnversionedSpriteFrame128:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_128
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_128
    .incbin "unversioned-sprite-128.bin"
UnversionedSpriteFrame129:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_129
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_129
    .incbin "unversioned-sprite-129.bin"
UnversionedSpriteFrame130:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_130
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_130
    .incbin "unversioned-sprite-130.bin"
UnversionedSpriteFrame131:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_131
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_131
    .incbin "unversioned-sprite-131.bin"
UnversionedSpriteFrame132:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_132
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_132
    .incbin "unversioned-sprite-132.bin"
UnversionedSpriteFrame133:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_133
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_133
    .incbin "unversioned-sprite-133.bin"
UnversionedSpriteFrame134:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_134
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_134
    .incbin "unversioned-sprite-134.bin"
UnversionedSpriteFrame135:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_135
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_135
    .incbin "unversioned-sprite-135.bin"
UnversionedSpriteFrame136:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_136
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_136
    .incbin "unversioned-sprite-136.bin"
UnversionedSpriteFrame137:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_137
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_137
    .incbin "unversioned-sprite-137.bin"
UnversionedSpriteFrame138:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_138
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_138
    .incbin "unversioned-sprite-138.bin"
UnversionedSpriteFrame139:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_139
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_139
    .incbin "unversioned-sprite-139.bin"
UnversionedSpriteFrame140:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_140
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_140
    .incbin "unversioned-sprite-140.bin"
UnversionedSpriteFrame141:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_141
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_141
    .incbin "unversioned-sprite-141.bin"
UnversionedSpriteFrame142:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_142
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_142
    .incbin "unversioned-sprite-142.bin"
UnversionedSpriteFrame143:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_143
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_143
    .incbin "unversioned-sprite-143.bin"
UnversionedSpriteFrame144:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_144
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_144
    .incbin "unversioned-sprite-144.bin"
UnversionedSpriteFrame145:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_145
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_145
    .incbin "unversioned-sprite-145.bin"
UnversionedSpriteFrame146:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_146
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_146
    .incbin "unversioned-sprite-146.bin"
UnversionedSpriteFrame147:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_147
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_147
    .incbin "unversioned-sprite-147.bin"
UnversionedSpriteFrame148:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_148
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_148
    .incbin "unversioned-sprite-148.bin"
UnversionedSpriteFrame149:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_149
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_149
    .incbin "unversioned-sprite-149.bin"
UnversionedSpriteFrame150:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_150
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_150
    .incbin "unversioned-sprite-150.bin"
UnversionedSpriteFrame151:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_151
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_151
    .incbin "unversioned-sprite-151.bin"
UnversionedSpriteFrame152:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_152
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_152
    .incbin "unversioned-sprite-152.bin"
UnversionedSpriteFrame153:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_153
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_153
    .incbin "unversioned-sprite-153.bin"
UnversionedSpriteFrame154:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_154
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_154
    .incbin "unversioned-sprite-154.bin"
UnversionedSpriteFrame155:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_155
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_155
    .incbin "unversioned-sprite-155.bin"
UnversionedSpriteFrame156:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_156
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_156
    .incbin "unversioned-sprite-156.bin"
UnversionedSpriteFrame157:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_157
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_157
    .incbin "unversioned-sprite-157.bin"
UnversionedSpriteFrame158:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_158
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_158
    .incbin "unversioned-sprite-158.bin"
UnversionedSpriteFrame159:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_159
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_159
    .incbin "unversioned-sprite-159.bin"
UnversionedSpriteFrame160:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_160
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_160
    .incbin "unversioned-sprite-160.bin"
UnversionedSpriteFrame161:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_161
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_161
    .incbin "unversioned-sprite-161.bin"
UnversionedSpriteFrame162:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_162
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_162
    .incbin "unversioned-sprite-162.bin"
UnversionedSpriteFrame163:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_163
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_163
    .incbin "unversioned-sprite-163.bin"
UnversionedSpriteFrame164:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_164
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_164
    .incbin "unversioned-sprite-164.bin"
UnversionedSpriteFrame165:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_165
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_165
    .incbin "unversioned-sprite-165.bin"
UnversionedSpriteFrame166:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_166
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_166
    .incbin "unversioned-sprite-166.bin"
UnversionedSpriteFrame167:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_167
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_167
    .incbin "unversioned-sprite-167.bin"
UnversionedSpriteFrame168:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_168
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_168
    .incbin "unversioned-sprite-168.bin"
UnversionedSpriteFrame169:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_169
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_169
    .incbin "unversioned-sprite-169.bin"
UnversionedSpriteFrame170:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_170
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_170
    .incbin "unversioned-sprite-170.bin"
UnversionedSpriteFrame171:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_171
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_171
    .incbin "unversioned-sprite-171.bin"
UnversionedSpriteFrame172:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_172
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_172
    .incbin "unversioned-sprite-172.bin"
UnversionedSpriteFrame173:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_173
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_173
    .incbin "unversioned-sprite-173.bin"
UnversionedSpriteFrame174:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_174
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_174
    .incbin "unversioned-sprite-174.bin"
UnversionedSpriteFrame175:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_175
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_175
    .incbin "unversioned-sprite-175.bin"
UnversionedSpriteFrame176:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_176
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_176
    .incbin "unversioned-sprite-176.bin"
UnversionedSpriteFrame177:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_177
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_177
    .incbin "unversioned-sprite-177.bin"
UnversionedSpriteFrame178:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_178
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_178
    .incbin "unversioned-sprite-178.bin"
UnversionedSpriteFrame179:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_179
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_179
    .incbin "unversioned-sprite-179.bin"
UnversionedSpriteFrame180:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_180
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_180
    .incbin "unversioned-sprite-180.bin"
UnversionedSpriteFrame181:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_181
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_181
    .incbin "unversioned-sprite-181.bin"
UnversionedSpriteFrame182:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_182
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_182
    .incbin "unversioned-sprite-182.bin"
UnversionedSpriteFrame183:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_183
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_183
    .incbin "unversioned-sprite-183.bin"
UnversionedSpriteFrame184:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_184
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_184
    .incbin "unversioned-sprite-184.bin"
UnversionedSpriteFrame185:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_185
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_185
    .incbin "unversioned-sprite-185.bin"
UnversionedSpriteFrame186:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_186
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_186
    .incbin "unversioned-sprite-186.bin"
UnversionedSpriteFrame187:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_187
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_187
    .incbin "unversioned-sprite-187.bin"
UnversionedSpriteFrame188:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_188
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_188
    .incbin "unversioned-sprite-188.bin"
UnversionedSpriteFrame189:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_189
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_189
    .incbin "unversioned-sprite-189.bin"
UnversionedSpriteFrame190:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_190
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_190
    .incbin "unversioned-sprite-190.bin"
UnversionedSpriteFrame191:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_191
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_191
    .incbin "unversioned-sprite-191.bin"
UnversionedSpriteFrame192:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_192
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_192
    .incbin "unversioned-sprite-192.bin"
UnversionedSpriteFrame193:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_193
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_193
    .incbin "unversioned-sprite-193.bin"
UnversionedSpriteFrame194:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_194
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_194
    .incbin "unversioned-sprite-194.bin"
UnversionedSpriteFrame195:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_195
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_195
    .incbin "unversioned-sprite-195.bin"
UnversionedSpriteFrame196:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_196
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_196
    .incbin "unversioned-sprite-196.bin"
UnversionedSpriteFrame197:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_197
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_197
    .incbin "unversioned-sprite-197.bin"
UnversionedSpriteFrame198:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_198
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_198
    .incbin "unversioned-sprite-198.bin"
UnversionedSpriteFrame199:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_199
    UnversionedSpriteFrameShape $04, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_199
    .incbin "unversioned-sprite-199.bin"
UnversionedSpriteFrame200:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_200
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_200
    .incbin "unversioned-sprite-200.bin"
UnversionedSpriteFrame201:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_201
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_201
    .incbin "unversioned-sprite-201.bin"
UnversionedSpriteFrame202:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_202
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_202
    .incbin "unversioned-sprite-202.bin"
UnversionedSpriteFrame203:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_203
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_203
    .incbin "unversioned-sprite-203.bin"
UnversionedSpriteFrame204:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_204
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_204
    .incbin "unversioned-sprite-204.bin"
UnversionedSpriteFrame205:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_205
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_205
    .incbin "unversioned-sprite-205.bin"
UnversionedSpriteFrame206:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_206
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_206
    .incbin "unversioned-sprite-206.bin"
UnversionedSpriteFrame207:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_207
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_207
    .incbin "unversioned-sprite-207.bin"
UnversionedSpriteFrame208:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_208
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_208
    .incbin "unversioned-sprite-208.bin"
UnversionedSpriteFrame209:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_209
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_209
    .incbin "unversioned-sprite-209.bin"
UnversionedSpriteFrame210:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_210
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_210
    .incbin "unversioned-sprite-210.bin"
UnversionedSpriteFrame211:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_211
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_211
    .incbin "unversioned-sprite-211.bin"
UnversionedSpriteFrame212:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_212
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_212
    .incbin "unversioned-sprite-212.bin"
UnversionedSpriteFrame213:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_213
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_213
    .incbin "unversioned-sprite-213.bin"
UnversionedSpriteFrame214:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_214
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_214
    .incbin "unversioned-sprite-214.bin"
UnversionedSpriteFrame215:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_215
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_215
    .incbin "unversioned-sprite-215.bin"
UnversionedSpriteFrame216:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_216
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_216
    .incbin "unversioned-sprite-216.bin"
UnversionedSpriteFrame217:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_217
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_217
    .incbin "unversioned-sprite-217.bin"
UnversionedSpriteFrame218:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_218
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_218
    .incbin "unversioned-sprite-218.bin"
UnversionedSpriteFrame219:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_219
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_219
    .incbin "unversioned-sprite-219.bin"
UnversionedSpriteFrame220:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_220
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_220
    .incbin "unversioned-sprite-220.bin"
UnversionedSpriteFrame221:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_221
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_221
    .incbin "unversioned-sprite-221.bin"
UnversionedSpriteFrame222:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_222
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_222
    .incbin "unversioned-sprite-222.bin"
UnversionedSpriteFrame223:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_223
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_223
    .incbin "unversioned-sprite-223.bin"
UnversionedSpriteFrame224:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_224
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_224
    .incbin "unversioned-sprite-224.bin"
UnversionedSpriteFrame225:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_225
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_225
    .incbin "unversioned-sprite-225.bin"
UnversionedSpriteFrame226:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_226
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_226
    .incbin "unversioned-sprite-226.bin"
UnversionedSpriteFrame227:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_227
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_227
    .incbin "unversioned-sprite-227.bin"
UnversionedSpriteFrame228:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_228
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_228
    .incbin "unversioned-sprite-228.bin"
UnversionedSpriteFrame229:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_229
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_229
    .incbin "unversioned-sprite-229.bin"
UnversionedSpriteFrame230:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_230
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_230
    .incbin "unversioned-sprite-230.bin"
UnversionedSpriteFrame231:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_231
    UnversionedSpriteFrameShape $01, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_231
    .incbin "unversioned-sprite-231.bin"
UnversionedSpriteFrame232:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_232
    UnversionedSpriteFrameShape $01, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_232
    .incbin "unversioned-sprite-232.bin"
UnversionedSpriteFrame233:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_233
    UnversionedSpriteFrameShape $01, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_233
    .incbin "unversioned-sprite-233.bin"
UnversionedSpriteFrame234:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_234
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_234
    .incbin "unversioned-sprite-234.bin"
UnversionedSpriteFrame235:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_235
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_235
    .incbin "unversioned-sprite-235.bin"
UnversionedSpriteFrame236:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_236
    UnversionedSpriteFrameShape $01, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_236
    .incbin "unversioned-sprite-236.bin"
UnversionedSpriteFrame237:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_237
    UnversionedSpriteFrameShape $01, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_237
    .incbin "unversioned-sprite-237.bin"
UnversionedSpriteFrame238:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_238
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_238
    .incbin "unversioned-sprite-238.bin"
UnversionedSpriteFrame239:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_239
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_239
    .incbin "unversioned-sprite-239.bin"
UnversionedSpriteFrame240:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_240
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_240
    .incbin "unversioned-sprite-240.bin"
UnversionedSpriteFrame241:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_241
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_241
    .incbin "unversioned-sprite-241.bin"
UnversionedSpriteFrame242:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_242
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_242
    .incbin "unversioned-sprite-242.bin"
UnversionedSpriteFrame243:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_243
    UnversionedSpriteFrameShape $03, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_243
    .incbin "unversioned-sprite-243.bin"
UnversionedSpriteFrame244:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_244
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_244
    .incbin "unversioned-sprite-244.bin"
UnversionedSpriteFrame245:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_245
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_245
    .incbin "unversioned-sprite-245.bin"
UnversionedSpriteFrame246:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_246
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_246
    .incbin "unversioned-sprite-246.bin"
UnversionedSpriteFrame247:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_247
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_247
    .incbin "unversioned-sprite-247.bin"
UnversionedSpriteFrame248:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_248
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_248
    .incbin "unversioned-sprite-248.bin"
UnversionedSpriteFrame249:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_249
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_249
    .incbin "unversioned-sprite-249.bin"
UnversionedSpriteFrame250:
    ObservedSpriteOamFlags $00, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_250
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_250
    .incbin "unversioned-sprite-250.bin"
UnversionedSpriteFrame251:
    ObservedSpriteOamFlags $00, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_251
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_251
    .incbin "unversioned-sprite-251.bin"
UnversionedSpriteFrame252:
    ObservedSpriteOamFlags $00, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_252
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_252
    .incbin "unversioned-sprite-252.bin"
UnversionedSpriteFrame253:
    ObservedSpriteOamFlags $00, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_253
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_253
    .incbin "unversioned-sprite-253.bin"
UnversionedSpriteFrame254:
    ObservedSpriteOamFlags $00, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_254
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_254
    .incbin "unversioned-sprite-254.bin"
UnversionedSpriteFrame255:
    ObservedSpriteOamFlags $00, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_255
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_255
    .incbin "unversioned-sprite-255.bin"
UnversionedSpriteFrame256:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_256
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_256
    .incbin "unversioned-sprite-256.bin"
UnversionedSpriteFrame257:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_257
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_257
    .incbin "unversioned-sprite-257.bin"
UnversionedSpriteFrame258:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_258
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_258
    .incbin "unversioned-sprite-258.bin"
UnversionedSpriteFrame259:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_259
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_259
    .incbin "unversioned-sprite-259.bin"
UnversionedSpriteFrame260:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_260
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_260
    .incbin "unversioned-sprite-260.bin"
UnversionedSpriteFrame261:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_261
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_261
    .incbin "unversioned-sprite-261.bin"
UnversionedSpriteFrame262:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_262
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_262
    .incbin "unversioned-sprite-262.bin"
UnversionedSpriteFrame263:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_263
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_263
    .incbin "unversioned-sprite-263.bin"
UnversionedSpriteFrame264:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_264
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_264
    .incbin "unversioned-sprite-264.bin"
UnversionedSpriteFrame265:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_265
    UnversionedSpriteFrameShape $02, $02 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_265
    .incbin "unversioned-sprite-265.bin"
UnversionedSpriteFrame266:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_266
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_266
    .incbin "unversioned-sprite-266.bin"
UnversionedSpriteFrame267:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_267
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_267
    .incbin "unversioned-sprite-267.bin"
UnversionedSpriteFrame268:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_268
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_268
    .incbin "unversioned-sprite-268.bin"
UnversionedSpriteFrame269:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_269
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_269
    .incbin "unversioned-sprite-269.bin"
UnversionedSpriteFrame270:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_270
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_270
    .incbin "unversioned-sprite-270.bin"
UnversionedSpriteFrame271:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_271
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_271
    .incbin "unversioned-sprite-271.bin"
UnversionedSpriteFrame272:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_272
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_272
    .incbin "unversioned-sprite-272.bin"
UnversionedSpriteFrame273:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_273
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_273
    .incbin "unversioned-sprite-273.bin"
UnversionedSpriteFrame274:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_274
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_274
    .incbin "unversioned-sprite-274.bin"
UnversionedSpriteFrame275:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_275
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_275
    .incbin "unversioned-sprite-275.bin"
UnversionedSpriteFrame276:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_276
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_276
    .incbin "unversioned-sprite-276.bin"
UnversionedSpriteFrame277:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_277
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_277
    .incbin "unversioned-sprite-277.bin"
UnversionedSpriteFrame278:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_278
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_278
    .incbin "unversioned-sprite-278.bin"
UnversionedSpriteFrame279:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_279
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_279
    .incbin "unversioned-sprite-279.bin"
UnversionedSpriteFrame280:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_280
    UnversionedSpriteFrameShape $04, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_280
    .incbin "unversioned-sprite-280.bin"
UnversionedSpriteFrame281:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_281
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_281
    .incbin "unversioned-sprite-281.bin"
UnversionedSpriteFrame282:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_282
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_282
    .incbin "unversioned-sprite-282.bin"
UnversionedSpriteFrame283:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_283
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_283
    .incbin "unversioned-sprite-283.bin"
UnversionedSpriteFrame284:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_284
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_284
    .incbin "unversioned-sprite-284.bin"
UnversionedSpriteFrame285:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_285
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_285
    .incbin "unversioned-sprite-285.bin"
UnversionedSpriteFrame286:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_286
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_286
    .incbin "unversioned-sprite-286.bin"
UnversionedSpriteFrame287:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_287
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_287
    .incbin "unversioned-sprite-287.bin"
UnversionedSpriteFrame288:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_288
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_288
    .incbin "unversioned-sprite-288.bin"
UnversionedSpriteFrame289:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_289
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_289
    .incbin "unversioned-sprite-289.bin"
UnversionedSpriteFrame290:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_290
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_290
    .incbin "unversioned-sprite-290.bin"
UnversionedSpriteFrame291:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_291
    UnversionedSpriteFrameShape $02, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_291
    .incbin "unversioned-sprite-291.bin"
UnversionedSpriteFrame292:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_292
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_292
    .incbin "unversioned-sprite-292.bin"
UnversionedSpriteFrame293:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_293
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_293
    .incbin "unversioned-sprite-293.bin"
UnversionedSpriteFrame294:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_294
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_294
    .incbin "unversioned-sprite-294.bin"
UnversionedSpriteFrame295:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_295
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_295
    .incbin "unversioned-sprite-295.bin"
UnversionedSpriteFrame296:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_296
    UnversionedSpriteFrameShape $03, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_296
    .incbin "unversioned-sprite-296.bin"
UnversionedSpriteFrame297:
    ObservedSpriteOamFlags $0A, $01 ; CONTROL_UNVERSIONED_SPRITE_FLAGS_297
    UnversionedSpriteFrameShape $01, $01 ; CONTROL_UNVERSIONED_SPRITE_SHAPE_297
    .incbin "unversioned-sprite-297.bin"
.assert * = $C582, error, "unversioned sprite region end"
