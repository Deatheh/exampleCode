package postgres

import (
	"database/sql"
	"fmt"
)

type AllTable struct {
	db *sql.DB // Указатель на подключение к базе данных
}

func (at *AllTable) GetAllUserType() ([]map[string]interface{}, error) {
	query := `SELECT 
    typname as type_name,
    typcategory as category
	FROM pg_type t
	JOIN pg_namespace n ON t.typnamespace = n.oid
	WHERE n.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
  	AND t.typtype IN ('c', 'e')`

	rows, err := at.db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("failed to get data from employee table: %v", err)
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

func (at *AllTable) GetAllUserTypeWithValues() ([]map[string]interface{}, error) {
	query := `WITH type_info AS (
    SELECT 
        t.oid,
        n.nspname as schema_name,
        t.typname as type_name,
        CASE t.typtype 
            WHEN 'c' THEN 'COMPOSITE'
            WHEN 'e' THEN 'ENUM'
            ELSE 'OTHER'
        END as type_kind
    FROM pg_type t
    JOIN pg_namespace n ON t.typnamespace = n.oid
    WHERE n.nspname NOT IN ('information_schema', 'pg_catalog')
      AND t.typtype IN ('c', 'e')
	),

enum_values AS (
    -- Значения ENUM типов
    SELECT 
        t.oid,
        json_agg(e.enumlabel ORDER BY e.enumsortorder) as values
    FROM pg_enum e
    JOIN pg_type t ON t.oid = e.enumtypid
    GROUP BY t.oid
),

composite_fields AS (
    -- Поля составных типов
    SELECT 
        t.oid,
        json_agg(
           a.attname
        ) as fields
    FROM pg_type t
    JOIN pg_class c ON c.oid = t.typrelid
    JOIN pg_attribute a ON a.attrelid = c.oid
    WHERE t.typtype = 'c'
      AND a.attnum > 0
      AND NOT a.attisdropped
    GROUP BY t.oid
)

SELECT 
    ti.type_name,
    ti.type_kind,
    ev.values as enum_values,
    cf.fields as composite_fields
FROM type_info ti
LEFT JOIN enum_values ev ON ti.oid = ev.oid AND ti.type_kind = 'ENUM'
LEFT JOIN composite_fields cf ON ti.oid = cf.oid AND ti.type_kind = 'COMPOSITE'
ORDER BY ti.schema_name, ti.type_name;`

	rows, err := at.db.Query(query)
	if err != nil {
		return nil, fmt.Errorf("failed to get data from employee table: %v", err)
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

func (at *AllTable) AddType(query string) error {
	at.db.QueryRow(query)
	return nil
}

func newAllTable(db *sql.DB) (*AllTable, error) {
	return &AllTable{db: db}, nil
}
