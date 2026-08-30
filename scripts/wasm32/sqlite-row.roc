app [Context, program] {
	pf: platform "../../platform/main.roc",
	http: "https://github.com/roc-lang/http/releases/download/1.0.0/6ZUwqYhCS8PU9Mo6MF7oV82ET2o7KYb57CLKDq4cq4sS.tar.zst",
}

import pf.Path
import pf.Server
import pf.Sqlite
import http.Response

Context : Sqlite.Db

program = { init!, respond!, shutdown! }

init! : () => Try({ config : Server.Config, context : Context }, [Exit(I64), ..])
init! = || {
	db =
		match Sqlite.open!(
			{
				path: Path.utf8(":memory:"),
				max_connections: 1,
				acquire_timeout_ms: 100,
				busy_timeout_ms: 1_000,
				max_cached_statements_per_connection: 32,
				journal_mode: Delete,
				synchronous: Full,
			},
		) {
			Ok(opened) => opened
			Err(_) => return Err(Exit(1))
		}
	match Sqlite.execute!(
		{
			db,
			query: "CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT NOT NULL)",
			params: {},
		},
	) {
		Ok({}) => {}
		Err(_) => return Err(Exit(1))
	}
	match Sqlite.execute!(
		{
			db,
			query: "INSERT INTO notes (body) VALUES ('hello-sqlite')",
			params: {},
		},
	) {
		Ok({}) => {}
		Err(_) => return Err(Exit(1))
	}
	Ok({ config: Server.default_config, context: db })
}

respond! : Server.Request, Context => Try(Server.Outcome, [ServerErr(Str), ..])
respond! = |_request, db| {
	row : { body : Str }
	row =
		match Sqlite.query!(
			{
				db,
				query: "SELECT body FROM notes ORDER BY id LIMIT 1",
				params: {},
				limits: Sqlite.default_query_limits,
			},
		) {
			Ok(found) => found
			Err(_) => return Err(ServerErr("query"))
		}
	Ok(Server.respond(Response.from_status(200).with_body(Str.to_utf8(row.body))))
}

shutdown! : Server.ShutdownReason, Context => Try({}, [Exit(I64), ..])
shutdown! = |_reason, _context| Ok({})
