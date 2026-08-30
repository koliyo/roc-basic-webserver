app [Context, program] {
	pf: platform "../../platform/main.roc",
	http: "https://github.com/roc-lang/http/releases/download/1.0.0/6ZUwqYhCS8PU9Mo6MF7oV82ET2o7KYb57CLKDq4cq4sS.tar.zst",
}

import pf.Env
import pf.Path
import pf.Server
import pf.Stderr
import http.Response

Context : {}

program = { init!, respond!, shutdown! }

init! : () => Try({ config : Server.Config, context : Context }, [Exit(I64), ..])
init! = || Ok({ config: Server.default_config, context: {} })

respond! : Server.Request, Context => Try(Server.Outcome, [ServerErr(Str), ..])
respond! = |_request, _context| {
	match Stderr.line!("env-log") {
		Ok({}) => {}
		Err(_) => {}
	}
	greeting =
		match Env.var!("GREETING") {
			Ok(value) => Path.display(Path.from_os_str(value))
			Err(_) => "missing"
		}
	Ok(Server.respond(Response.from_status(200).with_body(Str.to_utf8("<p>${greeting}</p>"))))
}

shutdown! : Server.ShutdownReason, Context => Try({}, [Exit(I64), ..])
shutdown! = |_reason, _context| Ok({})
