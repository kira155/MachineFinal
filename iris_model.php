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
    echo "✅ Prediksi Jenis Bunga: " . $result['prediction'];
}
?>
