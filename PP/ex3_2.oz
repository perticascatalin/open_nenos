% Take and Drop elements in a list
declare
fun {Take Xs N}
	case Xs
	of nil then nil
	[] H|T then
		if N == 0 then nil
		else H|{Take T N-1}
		end
	end
end

fun {Drop Xs N}
	case Xs
	of nil then nil
	[] H|T then
		if N == 0 then H|T
		else {Drop T N-1}
		end
	end
end

{Browse {Take [1 4 3 6 2] 3}}
{Browse {Drop [1 4 3 6 2] 3}}