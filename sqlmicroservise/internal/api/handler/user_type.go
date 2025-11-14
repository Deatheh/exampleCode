package handler

import (
	"fmt"
	"net/http"
	"notifications/internal/entities"

	"github.com/gofiber/fiber/v3"
)

func (h *Handler) HandlerGetAllUserType(c fiber.Ctx) error {
	data, err := h.services.All.GetAllTypes()
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusInternalServerError).JSON(err.Error())
	}
	return c.Status(http.StatusOK).JSON(data)
}

func (h *Handler) HandlerGetAllUserTypeWithValues(c fiber.Ctx) error {
	data, err := h.services.All.GetAllTypesWithValues()
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusInternalServerError).JSON(err.Error())
	}
	return c.Status(http.StatusOK).JSON(data)
}

func (h *Handler) HandlerAddType(c fiber.Ctx) error {
	var query entities.InputAlter
	err := c.Bind().JSON(&query)
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusBadRequest).JSON(err.Error())
	}
	err = h.services.All.AddType(query.AlterStrings)
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusInternalServerError).JSON(err.Error())

	}
	ans := entities.Message{
		Message: "ok",
	}
	return c.Status(http.StatusOK).JSON(ans)
}
