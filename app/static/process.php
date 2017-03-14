<?php

//proess.php

$errors = array();
$data = array();

//validate the variables -- 

if (empty($_POST['firstname']))
    $errors['firstname'] = 'Name is required';

if (empty($_POST['lastname']))
    $errors['firstname'] = 'Last name is required';

//return a response


//response if they are errors

if (! empty($errors)){
    $data['success'] = false
    $data['errors'] = $errors;
} else {
    // if there are no errors, return a message
    $data['success'] = true;
    $data['message'] = 'Success!';
}

echo json_encode($data);
