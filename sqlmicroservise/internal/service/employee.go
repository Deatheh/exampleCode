package service

import "notifications/internal/database/postgres"

type EmployeeService struct {
	repository *postgres.EmployeeTable
}

func (es EmployeeService) Add(kStr, vStr string) (int, error) {
	id, err := es.repository.Add(kStr, vStr)
	if err != nil {
		return 0, err
	}
	return id, nil
}

func (es EmployeeService) GetAll() ([]map[string]interface{}, error) {
	res, err := es.repository.GetAll()
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (es EmployeeService) GetAllByFilters(outputCol, joinStrings, whereStrings, groupByStrings, havingStrings, orderByStrings string) ([]map[string]interface{}, error) {
	res, err := es.repository.GetAllByFilters(outputCol, joinStrings, whereStrings, groupByStrings, havingStrings, orderByStrings)
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (es EmployeeService) AlterTable(AlterStrings string) error {
	err := es.repository.AlterTable(AlterStrings)
	if err != nil {
		return err
	}
	return nil
}

func (es EmployeeService) GetAllColumns() ([][]string, error) {
	res, err := es.repository.GetAllColumns()
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (es EmployeeService) GetAllConstrains() ([]string, error) {
	res, err := es.repository.GetAllConstraints()
	if err != nil {
		return nil, err
	}
	return res, nil
}
