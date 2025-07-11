package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin:     func(r *http.Request) bool { return true }, // Allow all origins for simplicity
}

type ChatRequest struct {
	Provider     string `json:"provider"`
	APIKey       string `json:"api_key"`
	Prompt       string `json:"prompt"`
	Model        string `json:"model,omitempty"`
	SystemPrompt string `json:"system_prompt,omitempty"`
}

func main() {
	r := gin.Default()

	r.Any("/ask", func(c *gin.Context) {
		conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
		if err != nil {
			log.Println("WebSocket upgrade failed:", err)
			return
		}
		defer conn.Close()

		// Read initial message from client
		_, msg, err := conn.ReadMessage()
		if err != nil {
			log.Println("Read error:", err)
			return
		}

		var req ChatRequest
		if err := json.Unmarshal(msg, &req); err != nil {
			conn.WriteMessage(websocket.TextMessage, []byte("Invalid request"))
			return
		}

		// Forward to FastAPI
		payload, _ := json.Marshal(req)
		resp, err := http.Post("http://localhost:8000/ai/chat", "application/json", bytes.NewBuffer(payload))
		if err != nil {
			conn.WriteMessage(websocket.TextMessage, []byte("AI service error"))
			return
		}
		defer resp.Body.Close()

		// Stream response back to client
		reader := resp.Body
		buf := make([]byte, 1024)
		for {
			n, err := reader.Read(buf)
			if err == io.EOF {
				break
			}
			if err != nil {
				log.Println("Stream error:", err)
				break
			}
			if err := conn.WriteMessage(websocket.TextMessage, buf[:n]); err != nil {
				log.Println("Write error:", err)
				break
			}
		}
	})

	r.Run(":8080")
}
