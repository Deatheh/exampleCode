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
	GetAllConstrains() ([]string, error)
}

type Project interface {
	Add(kStr, vStr string) (int, error)
	GetAll() ([]map[string]interface{}, error)
	GetAllByFilters(outputCol string) ([]map[string]interface{}, error)
	AlterTable(AlterStrings string) error
	GetAllColumns() ([][]string, error)
	GetAllConstraints() ([]string, error)
}

type Task interface {
	Add(kStr, vStr string) (int, error)
	GetAll() ([]map[string]interface{}, error)
	GetAllByFilters(outputCol, joinStrings, whereStrings, groupByStrings, havingStrings, orderByStrings string) ([]map[string]interface{}, error)
	AlterTable(AlterStrings string) error
	GetAllColumns() ([][]string, error)
	GetAllConstrains() ([]string, error)
}

type Drop interface {
	Drop() error
}

type All interface {
	GetAllTypes() ([]map[string]interface{}, error)
	AddType(queru string) error
	GetAllTypesWithValues() ([]map[string]interface{}, error)
}

type Service struct {
	Employee
	Project
	Task
	Drop
	All
}

func NewService(repository *database.Repository, envConf *config.Config) *Service {
	return &Service{
		Employee: &EmployeeService{repository: repository.DatabaseRepository.Employee},
		Project:  &ProjectService{repository: repository.DatabaseRepository.Project},
		Task:     &TaskService{repository: repository.DatabaseRepository.Task},
		Drop:     &DropService{repository: repository.DatabaseRepository.Drop},
		All:      &AllService{repository: repository.DatabaseRepository.All},
	}
}
