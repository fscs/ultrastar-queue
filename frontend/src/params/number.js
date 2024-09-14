/**
 * @param {string} param
 * @return {param is int}
 * @satisfies {import('@sveltejs/kit').ParamMatcher}
 */
export function match(param) {
	return Number.isInteger(parseInt(param))
}