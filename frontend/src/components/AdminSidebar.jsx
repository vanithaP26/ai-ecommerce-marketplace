import { Link } from "react-router-dom";

function AdminSidebar() {
  return (
    <div className="w-[260px] min-h-screen bg-black text-white p-6">
      <h1 className="text-3xl font-bold mb-10">
        AI Admin
      </h1>

      <div className="flex flex-col gap-6 text-lg">
        <Link to="/admin">
          Dashboard
        </Link>

        <Link to="/admin/categories">
          Categories
        </Link>

        <Link to="/admin/products">
          Products
        </Link>

        <Link to="/admin/orders">
          Orders
        </Link>

        <Link to="/admin/sellers">
          Sellers
        </Link>

        <Link to="/admin/customers">
          Customers
        </Link>
      </div>
    </div>
  );
}

export default AdminSidebar;