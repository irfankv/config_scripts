const a = 1

console.log(a)

let q = 2

function ab() {
    console.log("Iena")
    console.log("iaiiiaa")

}

function containsPurple(arr) {
    for (let color of arr) {
        if (color.toLowerCase() === 'purple' || color.toLowerCase() === 'magenta') {
            return true
        }
    }
    return false
}

arr = ["black", "purple", "Magenta"]

console.log(containsPurple(arr))

// function add(a, b) {
//     return a + b
// }

// console.log(add(2, 3))

function add(a, b, callback) {
    callback(a + b)
}

// function print(c) {
//     console.log(c)
// }

function print(c) {
    console.log(c)
}
var x = 5
var y = 4

add(x, y, function (c) {
    console.log(c)
})

add(x, y, (c) => {
    console.log(c)
})
add(x, y, (c) => console.log(c))