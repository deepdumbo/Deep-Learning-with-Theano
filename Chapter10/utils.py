import numpy
from theano import theano
import theano.tensor as T

def shared_zeros(shape, dtype=theano.config.floatX, name='', n=None):
    shape = shape if n is None else (n,) + shape
    return theano.shared(numpy.zeros(shape, dtype=dtype), name=name)

def shared_constant(shape,constant,dtype=theano.config.floatX, name='', n=None):
    return theano.shared(numpy.full(shape, constant, dtype=dtype))

def shared_glorot_uniform(shape, dtype=theano.config.floatX, name='', n=None):
    if isinstance(shape, int):
        high = numpy.sqrt(6. / shape)
    else:
        high = numpy.sqrt(6. / (numpy.sum(shape[:2]) * numpy.prod(shape[2:])))
    shape = shape if n is None else (n,) + shape
    return theano.shared(numpy.asarray(
        numpy.random.uniform(
            low=-high,
            high=high,
            size=shape),
        dtype=dtype), name=name)

def shared_uniform(shape, high, dtype=theano.config.floatX, name='', n=None):
    shape = shape if n is None else (n,) + shape
    return theano.shared(numpy.asarray(
        numpy.random.uniform(
            low=-high,
            high=high,
            size=shape),
        dtype=dtype), name=name)

def cast_floatX(n):
  return numpy.asarray(n, dtype=theano.config.floatX)

def get_dropout_noise(shape, dropout_p, _theano_rng):
    keep_p = 1 - dropout_p
    return cast_floatX(1. / keep_p) * _theano_rng.binomial(size=shape, p=keep_p, n=1, dtype=theano.config.floatX)

def save_params(outfile, params):
    l = []
    for param in params:
        l = l + [ param.get_value() ]
    numpy.savez(outfile, *l)
    print "Saved model parameters to {}.npz".format(outfile)

def load_params(path, params):
    npzfile = numpy.load(path+".npz")
    for i, param in enumerate(params):
        param.set_value( npzfile["arr_" +str(i)] )
    print "Loaded model parameters from {}.npz".format(path)


def get_noise_x(x, drop_x):
  """Get a random (variational) dropout noise matrix for input words.
  Return value is generated by the CPU (rather than directly on the GPU, as is done for other noise matrices).
  """
  batch_size, num_steps = x.shape
  keep_x = 1.0 - drop_x
  if keep_x < 1.0:
    noise_x = (numpy.random.random_sample((batch_size, num_steps)) < keep_x).astype(numpy.float32) / keep_x
    for b in range(batch_size):
      for n1 in range(num_steps):
        for n2 in range(n1 + 1, num_steps):
          if x[b][n2] == x[b][n1]:
            noise_x[b][n2] = noise_x[b][n1]
            break
  else:
    noise_x = numpy.ones((config.batch_size, config.num_steps), dtype=numpy.float32)
  return noise_x
