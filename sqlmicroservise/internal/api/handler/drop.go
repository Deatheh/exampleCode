package handler

import (
	"fmt"
	"net/http"

	"github.com/gofiber/fiber/v3"
)

func (h *Handler) HandlerDrop(c fiber.Ctx) error {
	err := h.services.Drop.Drop()
	if err != nil {
		fmt.Println(err.Error())
		return c.Status(http.StatusInternalServerError).JSON(err.Error())
	}
	c.Status(http.StatusOK)
	return nil
}
