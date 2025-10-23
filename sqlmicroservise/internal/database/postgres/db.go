package postgres

import (
	"database/sql"
	"fmt"
	"notifications/internal/config"

	_ "github.com/lib/pq"
)

var Database DatabaseRepository

type DatabaseRepository struct {
	Employee *EmployeeTable
	Project  *ProjectTable
	Task     *TaskTable
}

type TableModel interface {
	Add(*Entity) error
	GetById(*Entity) (*Entity, error)
}

type Entity interface {
	isDefault() bool
}

func NewDatabaseInstance(envConf *config.Config) *DatabaseRepository {

	connectionString := fmt.Sprintf(
		"host=%v port=%v user=%v password=%v dbname=%v sslmode=disable",
		envConf.Db.Host,
		envConf.Db.Port,
		envConf.Db.User,
		envConf.Db.Password,
		envConf.Db.Database)
	repository, err := Database.connectDatabase(connectionString)

	if err != nil {
		panic(err)
	}
	return repository
}

func (st *DatabaseRepository) connectDatabase(connectionString string) (*DatabaseRepository, error) {

	db, err := sql.Open("postgres", connectionString)
	if err != nil {
		return st, fmt.Errorf("could not connect to the database: %v", err)
	}

	err = db.Ping()
	if err != nil {
		return st, fmt.Errorf("could not ping the database: %v", err)
	}

	st.connectTables(db)

	return st, nil
}

// раздаем указатели на подключение декораторам
func (st *DatabaseRepository) connectTables(db *sql.DB) {
	var err error
	st.Employee, err = newEmployeeTable(db, createTableEmployee)
	if err != nil {
		panic(err)
	}
	st.Project, err = newProjectTable(db, createTableProject)
	if err != nil {
		panic(err)
	}
	st.Task, err = newTaskTable(db, createTableTask)
	if err != nil {
		panic(err)
	}
}
