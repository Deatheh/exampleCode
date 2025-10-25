package postgres

import (
	"database/sql"
	"fmt"
)

type DropTable struct {
	db *sql.DB // Указатель на подключение к базе данных
}

func (dt *DropTable) Drop() error {
	insertQuery := `
	DROP SCHEMA public CASCADE;
	CREATE SCHEMA public;
	`
	err := dt.db.QueryRow(insertQuery)

	if err != nil {
		return fmt.Errorf("Drop.drop: %v", err)
	}

	return nil
}

func newDropTable(db *sql.DB) (*DropTable, error) {
	return &DropTable{db: db}, nil
}
