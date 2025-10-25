package service

import "notifications/internal/database/postgres"

type ProjectService struct {
	repository *postgres.ProjectTable
}

func (ps ProjectService) Add(kStr, vStr string) (int, error) {
	id, err := ps.repository.Add(kStr, vStr)
	if err != nil {
		return 0, err
	}
	return id, nil
}

func (ps ProjectService) GetAll() ([]map[string]interface{}, error) {
	res, err := ps.repository.GetAll()
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (ps ProjectService) GetAllByFilters(outputCol string) ([]map[string]interface{}, error) {
	res, err := ps.repository.GetAllByFilters(outputCol)
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (ps ProjectService) AlterTable(AlterStrings string) error {
	err := ps.repository.AlterTable(AlterStrings)
	if err != nil {
		return err
	}
	return nil
}

func (ps ProjectService) GetAllColumns() ([][]string, error) {
	res, err := ps.repository.GetAllColumns()
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (ps ProjectService) GetAllConstraints() ([]string, error) {
	res, err := ps.repository.GetAllConstraints()
	if err != nil {
		return nil, err
	}
	return res, nil
}
