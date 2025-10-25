package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"notifications/internal/entities"
	"notifications/pkg/utils"

	"github.com/gofiber/fiber/v3"
)

func (h *Handler) HandlerAddTask(c fiber.Ctx) error {
	var result map[string]interface{}
	err := json.Unmarshal(c.Body(), &result)
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusBadRequest).JSON(err.Error())

	}
	kStr, vStr := utils.FormattingMapToSQLQuery(result)
	id, err := h.services.Task.Add(kStr, vStr)
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusInternalServerError).JSON(err.Error())

	}
	return c.Status(http.StatusOK).JSON(entities.Id{
		Id: id,
	})
}

func (h *Handler) HandlerGetAllTask(c fiber.Ctx) error {
	data, err := h.services.Task.GetAll()
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusInternalServerError).JSON(err.Error())
	}
	return c.Status(http.StatusOK).JSON(data)
}

func (h *Handler) HandlerAlterTableTask(c fiber.Ctx) error {
	var alter entities.InputAlter
	err := c.Bind().JSON(&alter)
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusBadRequest).JSON(err.Error())
	}
	err = h.services.Task.AlterTable(alter.AlterStrings)
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusInternalServerError).JSON(err.Error())
	}
	ans := entities.Message{
		Message: "ok",
	}
	return c.Status(http.StatusOK).JSON(ans)
}

func (h *Handler) HandlerGetAllTaskByFilters(c fiber.Ctx) error {
	outputCol := c.Query("col_string")
	if len(outputCol) == 0 {
		fmt.Println(outputCol)
		return c.Status(http.StatusBadRequest).JSON(fmt.Errorf("error getting task by filters: empty output columns"))
	}
	joinStrings := c.Query("join_string")
	whereStrings := c.Query("where_string")
	groupByStrings := c.Query("group_by_string")
	havingStrings := c.Query("having_string")
	orderByStrings := c.Query("order_by_string")

	data, err := h.services.Task.GetAllByFilters(outputCol, joinStrings, whereStrings, groupByStrings, havingStrings, orderByStrings)
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusInternalServerError).JSON(err.Error())
	}
	return c.Status(http.StatusOK).JSON(data)
}

func (h *Handler) HandlerColumnsTask(c fiber.Ctx) error {
	data, err := h.services.Task.GetAllColumns()
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusInternalServerError).JSON(err.Error())
	}
	return c.Status(http.StatusOK).JSON(data)
}

func (h *Handler) HandlerContsraintsTask(c fiber.Ctx) error {
	data, err := h.services.Task.GetAllConstrains()
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusInternalServerError).JSON(err.Error())
	}
	return c.Status(http.StatusOK).JSON(data)
}
