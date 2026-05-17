import {
  useEffect,
  useState,
} from "react";

import API from "../services/api";

import AdminSidebar from "../components/AdminSidebar";

function AdminOrders() {
  const [orders, setOrders] =
    useState([]);

  const fetchOrders =
    async () => {
      const res = await API.get(
        "/orders"
      );

      setOrders(res.data);
    };

  useEffect(() => {
    fetchOrders();
  }, []);

  const updateStatus = async (
    id,
    status
  ) => {
    await API.put(`/orders/${id}`, {
      status,
    });

    fetchOrders();
  };

  return (
    <div className="flex">
      <AdminSidebar />

      <div className="flex-1 p-10 bg-gray-100 min-h-screen">
        <h1 className="text-4xl font-bold mb-10">
          Orders
        </h1>

        <div className="space-y-6">
          {orders.map((order) => (
            <div
              key={order._id}
              className="bg-white p-6 rounded-xl shadow"
            >
              <h2 className="text-2xl font-bold">
                Customer:
                {" "}
                {order.user?.name}
              </h2>

              <p className="mt-2 text-lg">
                Total:
                {" "}
                ₹{order.totalPrice}
              </p>

              <p className="mt-2">
                Status:
                {" "}
                <span className="font-bold">
                  {order.status}
                </span>
              </p>

              <div className="flex gap-4 mt-5">
                <button
                  onClick={() =>
                    updateStatus(
                      order._id,
                      "Shipped"
                    )
                  }
                  className="bg-blue-500 text-white px-5 py-2 rounded-lg"
                >
                  Ship
                </button>

                <button
                  onClick={() =>
                    updateStatus(
                      order._id,
                      "Delivered"
                    )
                  }
                  className="bg-green-500 text-white px-5 py-2 rounded-lg"
                >
                  Deliver
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AdminOrders;