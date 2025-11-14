package service

import "notifications/internal/database/postgres"

type AllService struct {
	repository *postgres.AllTable
}

func (as AllService) GetAllTypes() ([]map[string]interface{}, error) {
	res, err := as.repository.GetAllUserType()
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (as AllService) GetAllTypesWithValues() ([]map[string]interface{}, error) {
	res, err := as.repository.GetAllUserTypeWithValues()
	if err != nil {
		return nil, err
	}
	return res, nil
}

func (as AllService) AddType(queru string) error {
	err := as.repository.AddType(queru)
	if err != nil {
		return err
	}
	return nil
}
