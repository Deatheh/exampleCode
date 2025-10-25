package service

import "notifications/internal/database/postgres"

type TaskService struct {
	repository *postgres.TaskTable
}

func (ts TaskService) Add(kStr, vStr string) (int, error) {
	id, err := ts.repository.Add(kStr, vStr)
	if err != nil {
		return 0, err
	}
	return id, nil
}

func (ts TaskService) GetAll() ([]map[string]interface{}, error) {
	res, err := ts.repository.GetAll()
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (ts TaskService) GetAllByFilters(outputCol, joinStrings, whereStrings, groupByStrings, havingStrings, orderByStrings string) ([]map[string]interface{}, error) {
	res, err := ts.repository.GetAllByFilters(outputCol, joinStrings, whereStrings, groupByStrings, havingStrings, orderByStrings)
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (ts TaskService) AlterTable(AlterStrings string) error {
	err := ts.repository.AlterTable(AlterStrings)
	if err != nil {
		return err
	}
	return nil
}

func (ts TaskService) GetAllColumns() ([][]string, error) {
	res, err := ts.repository.GetAllColumns()
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (ts TaskService) GetAllConstrains() ([]string, error) {
	res, err := ts.repository.GetAllConstraints()
	if err != nil {
		return nil, err
	}
	return res, nil
}
