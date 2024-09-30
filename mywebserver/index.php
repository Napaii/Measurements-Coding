<?php
// Database credentials
$servername = "localhost"; // or your DB server
$username = "root";
$password = "";
$dbname = "esp32_data";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Function to sanitize input data
function sanitize_input($data) {
    return htmlspecialchars(stripslashes(trim($data)));
}

// Check if the request method is POST (i.e., data sent from ESP32)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['uptime'])) {
        // Sanitize uptime value
        $uptime = sanitize_input($_POST['uptime']);

        // Validate that uptime is a number
        if (is_numeric($uptime)) {
            // Prepare and bind
            $stmt = $conn->prepare("INSERT INTO uptime_records (uptime_minutes) VALUES (?)");
            $stmt->bind_param("i", $uptime);

            if ($stmt->execute()) {
                echo "Uptime received: " . $uptime . " minutes";
            } else {
                http_response_code(500);
                echo "Database insertion failed.";
            }

            $stmt->close();
            $conn->close();
            exit;
        } else {
            // Invalid uptime value
            http_response_code(400);
            echo "Invalid uptime value.";
            exit;
        }
    } else {
        // Uptime not set in POST data
        http_response_code(400);
        echo "No uptime data received.";
        exit;
    }
}

// If GET request, display the latest uptime on the web page
$sql = "SELECT uptime_minutes, timestamp FROM uptime_records ORDER BY id DESC LIMIT 1";
$result = $conn->query($sql);

$displayUptime = "No uptime data available.";

if ($result->num_rows > 0) {
    $row = $result->fetch_assoc();
    $displayUptime = htmlspecialchars($row['uptime_minutes']) . " minutes (Last updated: " . $row['timestamp'] . ")";
} else {
    $displayUptime = "No uptime records found.";
}

$conn->close();
?>
<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Uptime</title>
</head>
<body>
    <h1>ESP32 Uptime</h1>
    <p>Latest Uptime: <?php echo $displayUptime; ?></p>
</body>
</html>
