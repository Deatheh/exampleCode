package utils

import "strconv"

func FormattingMapToSQLQuery(values map[string]interface{}) (string, string) {
	formattingKeyString := ""
	formattingValueString := ""
	for k, v := range values {
		formattingKeyString += k + ", "

		vStr, okStr := v.(string)
		if okStr {
			vStr = "'" + vStr + "'"
		}
		arr, okArr := v.([]interface{})
		if okArr {
			tStr := "["
			for i := 0; i < len(arr); i++ {
				tStr += "'" + arr[i].(string) + "', "
			}
			vStr = "ARRAY" + tStr[:len(tStr)-2] + "]"
		}
		vFloat, okFloat := v.(float64)
		if okFloat {
			vStr = strconv.Itoa(int(vFloat))
		}
		vBool, okBool := v.(bool)
		if okBool {
			if vBool == true {
				vStr = "true"
			} else {
				vStr = "false"
			}
		}
		formattingValueString += vStr + ", "
	}

	return formattingKeyString[:len(formattingKeyString)-2], formattingValueString[:len(formattingValueString)-2]
}
