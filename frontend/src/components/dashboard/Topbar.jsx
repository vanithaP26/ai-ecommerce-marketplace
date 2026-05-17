import {
  Bell,
  Search,
} from "lucide-react";

function Topbar({ title }) {
  const user = JSON.parse(
    localStorage.getItem("user")
  );

  return (
    <div className="bg-white rounded-2xl shadow px-8 py-5 flex justify-between items-center mb-8">

      {/* LEFT */}

      <div>
        <h1 className="text-3xl font-bold">
          {title}
        </h1>

        <p className="text-gray-500 mt-1">
          Welcome back, {user?.name}
        </p>
      </div>

      {/* RIGHT */}

      <div className="flex items-center gap-6">

        {/* SEARCH */}

        <div className="flex items-center bg-gray-100 px-4 py-3 rounded-xl w-[320px]">
          <Search
            size={20}
            className="text-gray-500"
          />

          <input
            type="text"
            placeholder="Search..."
            className="bg-transparent outline-none ml-3 w-full"
          />
        </div>

        {/* NOTIFICATIONS */}

        <button className="relative bg-gray-100 p-3 rounded-xl">
          <Bell size={22} />

          <span className="absolute top-2 right-2 bg-red-500 w-2 h-2 rounded-full"></span>
        </button>

        {/* PROFILE */}

        <div className="flex items-center gap-3 bg-gray-100 px-4 py-2 rounded-xl">
          <img
            src="https://i.pravatar.cc/100"
            alt="profile"
            className="w-12 h-12 rounded-full"
          />

          <div>
            <h3 className="font-semibold">
              {user?.name}
            </h3>

            <p className="text-sm text-gray-500 capitalize">
              {user?.role}
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}

export default Topbar;