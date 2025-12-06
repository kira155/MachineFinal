<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Prediksi Jenis Bunga (Iris)</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container py-4">
    <h2>🌸 Prediksi Jenis Bunga (Iris Dataset)</h2>
    <form method="POST" action="prediksi.php" class="row g-3">
        <div class="col-md-6">
            <label class="form-label">Sepal Length (cm)</label>
            <input type="number" step="0.1" name="sepal_length" class="form-control" required>
        </div>
        <div class="col-md-6">
            <label class="form-label">Sepal Width (cm)</label>
            <input type="number" step="0.1" name="sepal_width" class="form-control" required>
        </div>
        <div class="col-md-6">
            <label class="form-label">Petal Length (cm)</label>
            <input type="number" step="0.1" name="petal_length" class="form-control" required>
        </div>
        <div class="col-md-6">
            <label class="form-label">Petal Width (cm)</label>
            <input type="number" step="0.1" name="petal_width" class="form-control" required>
        </div>
        <div class="col-12">
            <button type="submit" class="btn btn-primary">Prediksi</button>
        </div>
    </form>
</body>
</html>
