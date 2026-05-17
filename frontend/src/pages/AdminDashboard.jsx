import Sidebar from "../components/dashboard/Sidebar";

function AdminDashboard() {
  return (
    <div className="flex">
      <Sidebar role="admin" />

      <div className="flex-1 p-10 bg-gray-100 min-h-screen">
        <h1 className="text-4xl font-bold mb-10">
          Admin Dashboard
        </h1>

        <div className="grid md:grid-cols-4 gap-8">
          <div className="bg-white p-8 rounded-xl shadow">
            <h2 className="text-2xl font-bold">
              Products
            </h2>

            <p className="text-4xl mt-4 text-blue-600">
              0
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow">
            <h2 className="text-2xl font-bold">
              Orders
            </h2>

            <p className="text-4xl mt-4 text-green-600">
              0
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow">
            <h2 className="text-2xl font-bold">
              Sellers
            </h2>

            <p className="text-4xl mt-4 text-purple-600">
              0
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow">
            <h2 className="text-2xl font-bold">
              Revenue
            </h2>

            <p className="text-4xl mt-4 text-red-600">
              ₹0
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;