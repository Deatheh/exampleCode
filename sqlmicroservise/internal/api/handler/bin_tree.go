package handler

import (
	"encoding/json"
	"fmt"
	"net/http"
	"notifications/internal/entities"
	"notifications/pkg/utils"

	"github.com/gofiber/fiber/v3"
)

func (h *Handler) HandlerAddBinTree(c fiber.Ctx) error {
	var result map[string]interface{}
	err := json.Unmarshal(c.Body(), &result)
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusBadRequest).JSON(err.Error())

	}
	kStr, vStr := utils.FormattingMapToSQLQuery(result)
	id, err := h.services.BinTree.Add(kStr, vStr)
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusInternalServerError).JSON(err.Error())

	}
	return c.Status(http.StatusOK).JSON(entities.Id{
		Id: id,
	})
}
