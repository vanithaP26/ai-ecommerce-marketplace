function SellerDashboard() {
  return (
    <div className="min-h-screen bg-gray-100 p-10">
      <h1 className="text-4xl font-bold mb-10">
        Seller Dashboard
      </h1>

      <div className="grid md:grid-cols-3 gap-8">
        <div className="bg-white p-8 rounded-xl shadow">
          <h2 className="text-2xl font-bold">
            Total Products
          </h2>

          <p className="text-4xl mt-4 text-blue-600">
            0
          </p>
        </div>

        <div className="bg-white p-8 rounded-xl shadow">
          <h2 className="text-2xl font-bold">
            Total Orders
          </h2>

          <p className="text-4xl mt-4 text-green-600">
            0
          </p>
        </div>

        <div className="bg-white p-8 rounded-xl shadow">
          <h2 className="text-2xl font-bold">
            Revenue
          </h2>

          <p className="text-4xl mt-4 text-purple-600">
            ₹0
          </p>
        </div>
      </div>
    </div>
  );
}

export default SellerDashboard;