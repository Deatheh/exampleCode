package service

import (
	"notifications/internal/config"
	"notifications/internal/database"
)

type Employee interface {
	Add(kStr, vStr string) (int, error)
	GetAll() ([]map[string]interface{}, error)
	GetAllByFilters(outputCol, joinStrings, whereStrings, groupByStrings, havingStrings, orderByStrings string) ([]map[string]interface{}, error)
	AlterTable(AlterStrings string) error
	GetAllColumns() ([][]string, error)
}

type Project interface {
	Add(kStr, vStr string) (int, error)
	GetAll() ([]map[string]interface{}, error)
	GetAllByFilters(outputCol, joinStrings, whereStrings, groupByStrings, havingStrings, orderByStrings string) ([]map[string]interface{}, error)
	AlterTable(AlterStrings string) error
	GetAllColumns() ([][]string, error)
}

type Task interface {
	Add(kStr, vStr string) (int, error)
	GetAll() ([]map[string]interface{}, error)
	GetAllByFilters(outputCol, joinStrings, whereStrings, groupByStrings, havingStrings, orderByStrings string) ([]map[string]interface{}, error)
	AlterTable(AlterStrings string) error
	GetAllColumns() ([][]string, error)
}

type Service struct {
	Employee
	Project
	Task
}

func NewService(repository *database.Repository, envConf *config.Config) *Service {
	return &Service{
		Employee: &EmployeeService{repository: repository.DatabaseRepository.Employee},
		Project:  &ProjectService{repository: repository.DatabaseRepository.Project},
		Task:     &TaskService{repository: repository.DatabaseRepository.Task},
	}
}
