-- HWP Automation API Objects
-- 자동 생성됨: Scripts/parse_automation_api.py

module HwpIdris.Automation.Objects

import Data.String

-- Automation Object 타입
public export
data AutomationObject
    = IANT
    | IANT_BOOL
    | IANT값을
    | IANT로
    | ICHITARO
    | ICODE
    | ICT_MODE
    | ID
    | IDCANCE
    | IDCANCEL
    | IDNO
    | IDOK
    | IDRETR
    | IDRETRY
    | IDSPATCH
    | IDYES
    | IDispatch
    | ID가
    | ID는
    | ID를
    | ID에
    | ID와
    | ID의
    | IF
    | IF형식으로
    | IGNORE_IDABORT
    | IGNORE_IDIGNORE
    | IGNORE_IDRETRY
    | IGNORE_MASK
    | IHw
    | IHwpObject
    | IHwpObject는
    | IHwpObject로부터
    | IHwpObject의
    | III
    | IMG
    | IN
    | IP
    | IPT
    | IRANG
    | ISPATCH
    | ISPATCH로
    | IT_BSTR
    | IT_I4
    | IT_UI1
    | IT_UI4
    | IT임을
    | IWORD
    | IXHwpCharacterShape
    | IXHwpDocument
    | IXHwpDocumentInfo
    | IXHwpDocuments
    | IXHwpDocuments의
    | IXHwpDocument의
    | IXHwpFind
    | IXHwpFormCheckButton
    | IXHwpFormCheckButtons
    | IXHwpFormComboBox
    | IXHwpFormComboBoxs
    | IXHwpFormEdit
    | IXHwpFormEdits
    | IXHwpFormPushButton
    | IXHwpFormPushButtons
    | IXHwpFormRadioButton
    | IXHwpFormRadioButtons
    | IXHwpMessageBox의
    | IXHwpObject
    | IXHwpParagraphShape
    | IXHwpPrint
    | IXHwpRange
    | IXHwpSelection
    | IXHwpSendMail
    | IXHwpSummaryInfo
    | IXHwpTabs
    | IXHwpTab오브젝트를
    | IXHwpWindow오브젝트를
    | IfDirt
    | IfDirty
    | ImageAutoCheck
    | ImagePath
    | IndexMark
    | InfoId
    | InfoId에
    | Info참고
    | Initialization
    | Inline
    | InsertCtrl에
    | InsertLock
    | InsertText
    | Insert를
    | Item
    | Item을
    | I에서는

-- Object 이름 문자열로 변환
public export
toString : AutomationObject -> String
toString IANT = "IANT"
toString IANT_BOOL = "IANT_BOOL"
toString IANT값을 = "IANT값을"
toString IANT로 = "IANT로"
toString ICHITARO = "ICHITARO"
toString ICODE = "ICODE"
toString ICT_MODE = "ICT_MODE"
toString ID = "ID"
toString IDCANCE = "IDCANCE"
toString IDCANCEL = "IDCANCEL"
toString IDNO = "IDNO"
toString IDOK = "IDOK"
toString IDRETR = "IDRETR"
toString IDRETRY = "IDRETRY"
toString IDSPATCH = "IDSPATCH"
toString IDYES = "IDYES"
toString IDispatch = "IDispatch"
toString ID가 = "ID가"
toString ID는 = "ID는"
toString ID를 = "ID를"
toString ID에 = "ID에"
toString ID와 = "ID와"
toString ID의 = "ID의"
toString IF = "IF"
toString IF형식으로 = "IF형식으로"
toString IGNORE_IDABORT = "IGNORE_IDABORT"
toString IGNORE_IDIGNORE = "IGNORE_IDIGNORE"
toString IGNORE_IDRETRY = "IGNORE_IDRETRY"
toString IGNORE_MASK = "IGNORE_MASK"
toString IHw = "IHw"
toString IHwpObject = "IHwpObject"
toString IHwpObject는 = "IHwpObject는"
toString IHwpObject로부터 = "IHwpObject로부터"
toString IHwpObject의 = "IHwpObject의"
toString III = "III"
toString IMG = "IMG"
toString IN = "IN"
toString IP = "IP"
toString IPT = "IPT"
toString IRANG = "IRANG"
toString ISPATCH = "ISPATCH"
toString ISPATCH로 = "ISPATCH로"
toString IT_BSTR = "IT_BSTR"
toString IT_I4 = "IT_I4"
toString IT_UI1 = "IT_UI1"
toString IT_UI4 = "IT_UI4"
toString IT임을 = "IT임을"
toString IWORD = "IWORD"
toString IXHwpCharacterShape = "IXHwpCharacterShape"
toString IXHwpDocument = "IXHwpDocument"
toString IXHwpDocumentInfo = "IXHwpDocumentInfo"
toString IXHwpDocuments = "IXHwpDocuments"
toString IXHwpDocuments의 = "IXHwpDocuments의"
toString IXHwpDocument의 = "IXHwpDocument의"
toString IXHwpFind = "IXHwpFind"
toString IXHwpFormCheckButton = "IXHwpFormCheckButton"
toString IXHwpFormCheckButtons = "IXHwpFormCheckButtons"
toString IXHwpFormComboBox = "IXHwpFormComboBox"
toString IXHwpFormComboBoxs = "IXHwpFormComboBoxs"
toString IXHwpFormEdit = "IXHwpFormEdit"
toString IXHwpFormEdits = "IXHwpFormEdits"
toString IXHwpFormPushButton = "IXHwpFormPushButton"
toString IXHwpFormPushButtons = "IXHwpFormPushButtons"
toString IXHwpFormRadioButton = "IXHwpFormRadioButton"
toString IXHwpFormRadioButtons = "IXHwpFormRadioButtons"
toString IXHwpMessageBox의 = "IXHwpMessageBox의"
toString IXHwpObject = "IXHwpObject"
toString IXHwpParagraphShape = "IXHwpParagraphShape"
toString IXHwpPrint = "IXHwpPrint"
toString IXHwpRange = "IXHwpRange"
toString IXHwpSelection = "IXHwpSelection"
toString IXHwpSendMail = "IXHwpSendMail"
toString IXHwpSummaryInfo = "IXHwpSummaryInfo"
toString IXHwpTabs = "IXHwpTabs"
toString IXHwpTab오브젝트를 = "IXHwpTab오브젝트를"
toString IXHwpWindow오브젝트를 = "IXHwpWindow오브젝트를"
toString IfDirt = "IfDirt"
toString IfDirty = "IfDirty"
toString ImageAutoCheck = "ImageAutoCheck"
toString ImagePath = "ImagePath"
toString IndexMark = "IndexMark"
toString InfoId = "InfoId"
toString InfoId에 = "InfoId에"
toString Info참고 = "Info참고"
toString Initialization = "Initialization"
toString Inline = "Inline"
toString InsertCtrl에 = "InsertCtrl에"
toString InsertLock = "InsertLock"
toString InsertText = "InsertText"
toString Insert를 = "Insert를"
toString Item = "Item"
toString Item을 = "Item을"
toString I에서는 = "I에서는"

-- Object 설명
public export
description : AutomationObject -> String
description IANT = "Automation Object"
description IANT_BOOL = "Automation Object"
description IANT값을 = "Automation Object"
description IANT로 = "Automation Object"
description ICHITARO = "Automation Object"
description ICODE = "Automation Object"
description ICT_MODE = "Automation Object"
description ID = "Automation Object"
description IDCANCE = "Automation Object"
description IDCANCEL = "Automation Object"
description IDNO = "Automation Object"
description IDOK = "Automation Object"
description IDRETR = "Automation Object"
description IDRETRY = "Automation Object"
description IDSPATCH = "Automation Object"
description IDYES = "Automation Object"
description IDispatch = "Automation Object"
description ID가 = "Automation Object"
description ID는 = "Automation Object"
description ID를 = "Automation Object"
description ID에 = "Automation Object"
description ID와 = "Automation Object"
description ID의 = "Automation Object"
description IF = "Automation Object"
description IF형식으로 = "Automation Object"
description IGNORE_IDABORT = "Automation Object"
description IGNORE_IDIGNORE = "Automation Object"
description IGNORE_IDRETRY = "Automation Object"
description IGNORE_MASK = "Automation Object"
description IHw = "Automation Object"
description IHwpObject = "최상위 Automation Object"
description IHwpObject는 = "Automation Object"
description IHwpObject로부터 = "Automation Object"
description IHwpObject의 = "Automation Object"
description III = "Automation Object"
description IMG = "Automation Object"
description IN = "Automation Object"
description IP = "Automation Object"
description IPT = "Automation Object"
description IRANG = "Automation Object"
description ISPATCH = "Automation Object"
description ISPATCH로 = "Automation Object"
description IT_BSTR = "Automation Object"
description IT_I4 = "Automation Object"
description IT_UI1 = "Automation Object"
description IT_UI4 = "Automation Object"
description IT임을 = "Automation Object"
description IWORD = "Automation Object"
description IXHwpCharacterShape = "Automation Object"
description IXHwpDocument = "단일 문서 Object"
description IXHwpDocumentInfo = "Automation Object"
description IXHwpDocuments = "문서 Collection Object"
description IXHwpDocuments의 = "Automation Object"
description IXHwpDocument의 = "Automation Object"
description IXHwpFind = "Automation Object"
description IXHwpFormCheckButton = "Automation Object"
description IXHwpFormCheckButtons = "Automation Object"
description IXHwpFormComboBox = "Automation Object"
description IXHwpFormComboBoxs = "Automation Object"
description IXHwpFormEdit = "Automation Object"
description IXHwpFormEdits = "Automation Object"
description IXHwpFormPushButton = "Automation Object"
description IXHwpFormPushButtons = "Automation Object"
description IXHwpFormRadioButton = "Automation Object"
description IXHwpFormRadioButtons = "Automation Object"
description IXHwpMessageBox의 = "Automation Object"
description IXHwpObject = "Automation Object"
description IXHwpParagraphShape = "Automation Object"
description IXHwpPrint = "Automation Object"
description IXHwpRange = "Automation Object"
description IXHwpSelection = "Automation Object"
description IXHwpSendMail = "Automation Object"
description IXHwpSummaryInfo = "Automation Object"
description IXHwpTabs = "Automation Object"
description IXHwpTab오브젝트를 = "Automation Object"
description IXHwpWindow오브젝트를 = "Automation Object"
description IfDirt = "Automation Object"
description IfDirty = "Automation Object"
description ImageAutoCheck = "Automation Object"
description ImagePath = "Automation Object"
description IndexMark = "Automation Object"
description InfoId = "Automation Object"
description InfoId에 = "Automation Object"
description Info참고 = "Automation Object"
description Initialization = "Automation Object"
description Inline = "Automation Object"
description InsertCtrl에 = "Automation Object"
description InsertLock = "Automation Object"
description InsertText = "Automation Object"
description Insert를 = "Automation Object"
description Item = "Automation Object"
description Item을 = "Automation Object"
description I에서는 = "Automation Object"

-- 총 93개 Automation Object
