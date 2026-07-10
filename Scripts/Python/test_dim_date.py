from Generators.generate_dim_date import DimDateGenerator

generator = DimDateGenerator()

df = generator.generate()

print(df.shape)
print(df.head())
print(df.tail())
print(df.dtypes)