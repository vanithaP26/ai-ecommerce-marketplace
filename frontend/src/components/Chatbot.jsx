import { useState } from "react";

function Chatbot() {
  const [open, setOpen] = useState(false);

  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello 👋 Welcome to AI Shop!",
    },
  ]);

  const [input, setInput] = useState("");

  const sendMessage = () => {
    if (!input) return;

    const userMessage = {
      sender: "user",
      text: input,
    };

    let botReply = "I can help you shop products.";

    if (
      input.toLowerCase().includes("laptop")
    ) {
      botReply =
        "We have Gaming Laptops available.";
    }

    if (
      input.toLowerCase().includes("price")
    ) {
      botReply =
        "You can check latest product prices on product pages.";
    }

    if (
      input.toLowerCase().includes("delivery")
    ) {
      botReply =
        "Delivery usually takes 3-5 days.";
    }

    const botMessage = {
      sender: "bot",
      text: botReply,
    };

    setMessages([
      ...messages,
      userMessage,
      botMessage,
    ]);

    setInput("");
  };

  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 bg-black text-white w-16 h-16 rounded-full shadow-xl text-2xl"
      >
        💬
      </button>

      {open && (
        <div className="fixed bottom-24 right-6 w-[350px] bg-white rounded-xl shadow-2xl overflow-hidden">
          <div className="bg-black text-white p-4 text-xl font-bold">
            AI Assistant
          </div>

          <div className="h-[400px] overflow-y-auto p-4 space-y-4">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`p-3 rounded-xl max-w-[80%] ${
                  msg.sender === "user"
                    ? "bg-blue-500 text-white ml-auto"
                    : "bg-gray-200 text-black"
                }`}
              >
                {msg.text}
              </div>
            ))}
          </div>

          <div className="flex border-t">
            <input
              type="text"
              placeholder="Ask something..."
              value={input}
              onChange={(e) =>
                setInput(e.target.value)
              }
              className="flex-1 p-3 outline-none"
            />

            <button
              onClick={sendMessage}
              className="bg-black text-white px-6"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export default Chatbot;