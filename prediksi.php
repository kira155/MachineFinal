<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $data = [
        "sepal_length" => (float)$_POST['sepal_length'],
        "sepal_width"  => (float)$_POST['sepal_width'],
        "petal_length" => (float)$_POST['petal_length'],
        "petal_width"  => (float)$_POST['petal_width']
    ];

    $ch = curl_init("http://127.0.0.1:5000/predict");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));

    $response = curl_exec($ch);
    curl_close($ch);

    $result = json_decode($response, true);
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hasil Prediksi</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container py-4">
    <h2>📊 Hasil Prediksi</h2>
    <?php if (!empty($result['prediction'])): ?>
        <div class="alert alert-success">
            ✅ Jenis Bunga: <b><?= htmlspecialchars($result['prediction']) ?></b>
        </div>
    <?php else: ?>
        <div class="alert alert-danger">❌ Prediksi gagal!</div>
    <?php endif; ?>
    <a href="form_prediksi.php" class="btn btn-secondary">🔙 Kembali</a>
</body>
</html>
