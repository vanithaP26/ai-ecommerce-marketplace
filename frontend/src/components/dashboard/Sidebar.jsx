import {
  LayoutDashboard,
  ShoppingBag,
  Users,
  Package,
  ShoppingCart,
  BarChart3,
  Settings,
  LogOut,
  Tags,
} from "lucide-react";

import { Link } from "react-router-dom";

function Sidebar({ role }) {
  return (
    <div className="w-[270px] min-h-screen bg-[#111827] text-white p-6 flex flex-col justify-between">
      
      <div>
        <h1 className="text-3xl font-bold mb-10">
          AI Commerce
        </h1>

        <div className="space-y-3">

          <Link
            to={
              role === "admin"
                ? "/admin"
                : "/seller"
            }
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#1f2937] transition"
          >
            <LayoutDashboard size={20} />

            Dashboard
          </Link>

          <Link
            to={
              role === "admin"
                ? "/admin/products"
                : "/seller/products"
            }
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#1f2937] transition"
          >
            <ShoppingBag size={20} />

            Products
          </Link>

          <Link
            to={
              role === "admin"
                ? "/admin/orders"
                : "/seller/orders"
            }
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#1f2937] transition"
          >
            <ShoppingCart size={20} />

            Orders
          </Link>

          {role === "admin" && (
            <>
              <Link
                to="/admin/categories"
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#1f2937] transition"
              >
                <Tags size={20} />

                Categories
              </Link>

              <Link
                to="/admin/users"
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#1f2937] transition"
              >
                <Users size={20} />

                Users
              </Link>
            </>
          )}

          {role === "seller" && (
            <>
              <Link
                to="/seller/analytics"
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#1f2937] transition"
              >
                <BarChart3 size={20} />

                Analytics
              </Link>

              <Link
                to="/seller/store"
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#1f2937] transition"
              >
                <Package size={20} />

                Store
              </Link>
            </>
          )}

          <Link
            to="/settings"
            className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#1f2937] transition"
          >
            <Settings size={20} />

            Settings
          </Link>
        </div>
      </div>

      <button
        className="flex items-center gap-3 p-3 rounded-lg bg-red-500 hover:bg-red-600 transition"
        onClick={() => {
          localStorage.clear();

          window.location.href = "/login";
        }}
      >
        <LogOut size={20} />

        Logout
      </button>
    </div>
  );
}

export default Sidebar;