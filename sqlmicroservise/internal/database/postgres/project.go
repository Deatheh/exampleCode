package postgres

import (
	"database/sql"
	"fmt"
)

type ProjectTable struct {
	db *sql.DB // Указатель на подключение к базе данных
}

func (pt *ProjectTable) Add(columns, values string) (int, error) {
	insertQuery := fmt.Sprintf(`
	INSERT INTO project (%s)
		VALUES (%s)
		RETURNING id
	`, columns, values)
	var id int
	err := pt.db.QueryRow(insertQuery).Scan(&id)

	if err != nil {
		return 0, fmt.Errorf("Project.Add: %v", err)
	}

	return id, nil
}

func (pt *ProjectTable) GetAll() ([]map[string]interface{}, error) {
	query := `
	SELECT * FROM project
	`
	rows, err := pt.db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("failed to get data from project table: %v", err)
	}

	defer rows.Close()

	columns, err := rows.Columns()
	if err != nil {
		return nil, err
	}

	var results []map[string]interface{}

	for rows.Next() {
		values := make([]interface{}, len(columns))
		scanArgs := make([]interface{}, len(columns))

		for i := range values {
			scanArgs[i] = &values[i]
		}

		err := rows.Scan(scanArgs...)
		if err != nil {
			return nil, err
		}

		rowMap := make(map[string]interface{})
		for i, col := range columns {
			switch v := values[i].(type) {
			case []byte:
				rowMap[col] = string(v)
			default:
				rowMap[col] = v
			}
		}

		results = append(results, rowMap)
	}

	return results, nil
}

func (pt *ProjectTable) GetAllByFilters(outputCol, joinStrings, whereStrings, groupByStrings, havingStrings, orderByStrings string) ([]map[string]interface{}, error) {
	query := fmt.Sprintf(`
	SELECT %s FROM project
		`, outputCol)
	query += joinStrings
	query += whereStrings
	query += groupByStrings
	query += havingStrings
	query += orderByStrings

	rows, err := pt.db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("failed to get data from project table: %v", err)
	}

	defer rows.Close()

	columns, err := rows.Columns()
	if err != nil {
		return nil, err
	}

	var results []map[string]interface{}

	for rows.Next() {
		values := make([]interface{}, len(columns))
		scanArgs := make([]interface{}, len(columns))

		for i := range values {
			scanArgs[i] = &values[i]
		}

		err := rows.Scan(scanArgs...)
		if err != nil {
			return nil, err
		}

		rowMap := make(map[string]interface{})
		for i, col := range columns {
			switch v := values[i].(type) {
			case []byte:
				rowMap[col] = string(v)
			default:
				rowMap[col] = v
			}
		}

		results = append(results, rowMap)
	}

	return results, nil
}

func (pt *ProjectTable) AlterTable(alterStrings string) error {
	query := `
	ALTER TABLE project
	`
	query += alterStrings

	pt.db.QueryRow(query)

	return nil
}

func (pt *ProjectTable) GetAllColumns() ([][]string, error) {
	query := `
	SELECT 
		c.column_name, 
		c.is_nullable,
		CASE 
			WHEN c.data_type = 'USER-DEFINED' THEN pgt.typname
			ELSE c.data_type 
		END as data_type
	FROM information_schema.columns c
	LEFT JOIN pg_attribute pa ON c.table_name = pa.attrelid::regclass::text 
		AND c.column_name = pa.attname
	LEFT JOIN pg_type pgt ON pa.atttypid = pgt.oid
	WHERE c.table_name = 'project';
	`
	rows, err := pt.db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("failed to get columns project table: %v", err)
	}
	defer rows.Close()

	var columns [][]string

	for rows.Next() {
		var col []string
		var c, n, t string
		err := rows.Scan(&c, &n, &t)
		col = append(col, c)
		col = append(col, n)
		col = append(col, t)
		if err != nil {
			return nil, fmt.Errorf("Project.getAllColumns: %v", err)
		}
		columns = append(columns, col)
	}

	return columns, nil
}

func newProjectTable(db *sql.DB, query string) (*ProjectTable, error) {
	_, err := db.Exec(query)
	if err != nil {
		return nil, fmt.Errorf("failed to create project table: %v", err)
	}
	return &ProjectTable{db: db}, nil
}
