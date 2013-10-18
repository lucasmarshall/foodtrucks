import urllib, urllib2, copy, json, os, urlparse
from redis_cache import SimpleCache, cache_it

redis_conf = urlparse.urlparse(os.getenv('REDISTOGO_URL', 'redis://redistogo:42a7d091c0e7fbe5608e71d37c0b90cd@beardfish.redistogo.com:10647/'))
cache      = SimpleCache(limit=100, expire=60 * 60, hashkeys=True, host=redis_conf.hostname, port=redis_conf.port, password=redis_conf.password)

class SodaQuery(object):
	"""
	Generate a query string for querying a SODA API

	See: http://dev.socrata.com/docs/queries
	"""

	__operator_mapping = {
		'gt' : '>',
		'lt' : '<',
		'gte': '>=',
		'lte': '<=',
		'eq' : '=',
	}

	def __init__(self, endpoint):
		self.__endpoint = endpoint
		self.__where    = {}
		self.__select   = []
		self.__order    = None
		self.__limit    = None
		self.__offset   = None


	def where(self, **kwargs):
		"""
		Add a where clause to a query.

	    Only supports ANDing the query parts for now.
		Keyword arguments should be the field to include in the query, with an optional operator
		If an operator is not specified, it defaults to __eq

		Example:
		To generate a query like SELECT * WHERE age > 32, do:
		query.where(age__gt = 32)

		Supported operators include:
		field__gt             = field > value
		field__not_gt         = NOT field > value
		field__lt             = field < value
		field__not_lt         = NOT field < value
		field__gte            = field >= value
		field__not_ge         = NOT field >= value
		field__lte            = field <= value
		field__not_le         = NOT field <= value
		field__eq             = field = value
		field__not_eq         = NOT field = value
		field__null           = is null if value is True, is not null if value is False
		field__within_box     = geolocate field within the box described by the value: a sequence of 4 coordinates
		field__not_within_box = geolocate field NOT within the box described by the value: a sequence of 4 coordinates
		"""
		obj = copy.deepcopy(self)
		obj.__where.update(kwargs)
		return obj

	def select(self, *args):
		""" Add a select clause to a query """
		obj = copy.deepcopy(self)
		obj.__select.extend(args)
		return obj

	def order(self, order):
		"""
		Order the query by the field provided.

		For an acending order, just provide the field: 'distance'
		For decending order, precede the fieldname with a minus: '-distance'
		"""
		obj         = copy.deepcopy(self)
		obj.__order = order
		return obj

	def limit(self, limit):
		""" Limit the number of results to the number provided """
		obj         = copy.deepcopy(self)
		obj.__limit = limit
		return obj

	def offset(self, offset):
		""" Only the results in the set from the offset onward """
		obj          = copy.deepcopy(self)
		obj.__offset = offset
		return obj

	def execute(self):
		""" Execute the query """
		query = self.__build_query()
		return self.__do_query(query)

	@cache_it(cache=cache)
	def __do_query(self, query):
		response = self.__do_request(query)

		if response.getcode() == 200:
			try:
				return json.loads(response.read())
			except ValueError:
				SodaError("Couldn't decode JSON response")

		raise SodaError("Can't fetch URL %s, got HTTP code %s" % (response.geturl(), reponse.getcode()))

	def __do_request(self, query):
		print self.__endpoint + '?' + urllib.urlencode(query)
		try:
			return urllib2.urlopen(self.__endpoint + '?' + urllib.urlencode(query))
		except urllib2.URLError, e:
			raise SodaError("Can't fetch URL %s?%s: %s" % (self.__endpoint, urllib.urlencode(query), e))

	def __getitem__(self, key):
		""" Allow slicing - only supports up to 2 element slicing and positive indices, so no skipping! """
		obj = self
		try:
			if key.start is not None:
				assert key.start > 0, "Only positive indices are supported"
			if key.stop is not None:
				assert key.stop > 0,  "Only positive indices are supported"
				obj = obj.limit((key.stop - key.start) if key.start is not None else key.stop)
		except (AttributeError, TypeError):
			obj = obj.offset(key)
			obj = obj.limit(1)

		return obj

	def __build_query(self):
		query = {}

		if len(self.__where):
			query['$where'] = self.__build_where()

		if len(self.__select):
			query['$select'] = self.__build_select()

		if self.__order is not None:
			query['$order'] = self.__build_order()

		if self.__offset is not None:
			query['$offset'] = self.__offset

		if self.__limit is not None:
			query['$limit'] = self.__limit

		return query

	def __build_where(self):
		queries = []
		for field, value in self.__where.iteritems():
			operator = 'eq'
			parts    = field.rsplit('__', 1)
			do_not   = False
			if len(parts) == 2:
				field, operator = parts

			if operator[0:4] == 'not_':
				do_not = True
				_, operator = operator.split('_')

			# special case for __within_box
			if operator == 'within_box':
				assert (isinstance(value, list) and len(value) == 4), "__within_box queries must be a sequence of four coordinates"
				queries.append('within_box(%s,%s)' % (field, ','.join(value)))
				continue

			# special case for __null
			if operator == 'null':
				query = "%s IS NULL" if value else "%s IS NOT NULL"
				queries.append(query % field)
				continue

			operator = self.__get_operator(operator)

			queries.append("%s%s %s '%s'" % ("NOT " if do_not else "", field, operator, value))

		return ' AND '.join(queries)

	def __build_select(self):
		return ', '.join(self.__select)

	def __build_order(self):
		if self.__order[0] == '-':
			return '%s DESC' % self.__order[1:]

		return self.__order


	def __get_operator(self, operator):
		try:
			return self.__operator_mapping[operator]
		except KeyError:
			raise KeyError("Invalid operator %s" % operator)

class SodaError(Exception):
	pass
